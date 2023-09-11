import numpy as np
from locust import TaskSet, task, HttpUser, constant, LoadTestShape, events
from dataset import CabspottingUserFactory, TelecomUserFactory, TDriveUserFactory, UserFactory

json_data = {
    'network': {'url': 'https://sample-videos.com/img/Sample-jpg-image-50kb.jpg'},
    'dynamic_html': {'username': 'dragonbanana', 'random_len': 80000},
    'thumbnailer': {'url': 'https://sample-videos.com/img/Sample-jpg-image-50kb.jpg', 'width': 10, 'height': 10,
                    'n': 30000},
    'compression': {'url': 'https://cdn.bestmovie.it/wp-content/uploads/2020/05/winnie-the-pooh-disney-plus-HP.jpg',
                    'compression_mode': 1000},
}

# The workload is designed as an edge workload
# Some variables are just needed to instantiate the workload
# But they are not required for a cloud workload
node_coordinates = np.array([
    [0.25, 0.25],
    [0.75, 0.75],
])
functions = [
    "compression",
    "dynamic_html",
    "network",
    "thumbnailer"
]
functions_weights = np.array([
    0.5, 0.5
])
functions_weights = functions_weights / sum(functions_weights)

active_function_schedule = [
                               ['A', 'B'],
                               ['B', 'C'],
                               ['C', 'D'],
                               ['D', 'A'],
                           ] * 2

active_functions = ['A', 'B']

function_mapping = {
    'A': 'compression',
    'B': 'dynamic_html',
    'C': 'network',
    'D': 'thumbnailer',
}

port_mapping = {
    'compression': 31080,
    'dynamic_html': 31081,
    'network': 31082,
    'thumbnailer': 31083,
}


class UserTasks(TaskSet):

    @task
    def request(self):
        global active_functions
        function = np.random.choice(active_functions)
        function_name = function_mapping[function]
        function_port = port_mapping[function_name]
        # In-cluster
        #self.client.post(f"http://{function_name}.default.svc.cluster.local:80/function/{function_name}", json=json_data[function_name])
        # Outside cluster
        #self.client.post(f"http://<Public_IP_Address>:{function_port}/function/{function_name}", json=json_data[function_name])
        self.client.post(f"http://localhost:{function_port}/function/{function_name}", json=json_data[function_name])


class WebsiteUser(HttpUser):
    wait_time = constant(1)
    tasks = [UserTasks]


class CustomShape(LoadTestShape):
    time_limit = 0
    user_factory: UserFactory

    def tick(self):
        global active_functions
        current_time = round(self.get_run_time())
        if current_time < self.time_limit:
            normalized_time = current_time / self.time_limit
            users = self.user_factory.get_workload(normalized_time)
            active_functions = active_function_schedule[int(normalized_time * (len(active_function_schedule) - 0.01))]
            n_users = users.sum()
            return round(n_users), 1
        else:
            return None


@events.init_command_line_parser.add_listener
def _(parser):
    # A "--host" argument is needed but it might be overridden
    parser.add_argument("--duration", default=1800, type=int)
    parser.add_argument("--workload", type=str)
    args_dict = vars(parser.parse_args())
    print(args_dict)
    CustomShape.time_limit = args_dict['duration']

    if args_dict['workload'] == "cabspotting":
        CustomShape.user_factory = CabspottingUserFactory("cabspottingdata", node_coordinates, functions_weights)
    elif args_dict['workload'] == "tdrive":
        CustomShape.user_factory = TDriveUserFactory("tdrive", node_coordinates, functions_weights)
    elif args_dict['workload'] == "telecom":
        CustomShape.user_factory = TelecomUserFactory("telecom", node_coordinates, functions_weights)
    else:
        raise Exception(f"not valid workload {args_dict['workload']}")
    #UserTasks.mode = args_dict['mode']
    #UserTasks.req_session = args_dict['req_session']


@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response,
                       context, exception, start_time, url, **kwargs):
    if exception:
        print(f"Request to {name} with url {url} failed with exception {exception}")
