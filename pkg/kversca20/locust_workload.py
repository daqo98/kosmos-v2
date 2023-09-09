from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
    @task
    def get_root(self):
        # replace with the URL of your server
        self.client.get("http://localhost:80/prime/12")
        #self.client.get("http://54.220.175.10:31512/prime/12")
        


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class StagesShape(LoadTestShape):
    """
    A simply load test shape class that has different user and spawn_rate at
    different stages.
    Keyword arguments:
        stages -- A list of dicts, each representing a stage with the following keys:
            duration -- When this many seconds pass the test is advanced to the next stage
            users -- Total user count
            spawn_rate -- Number of users to start/stop per second
            stop -- A boolean that can stop that test at a specific stage
        stop_at_end -- Can be set to stop once all stages have run.
    """

    stages = [
        {"duration": 15, "users": 10, "spawn_rate": 10},
        {"duration": 50, "users": 0, "spawn_rate": 10},
        {"duration": 60, "users": 10, "spawn_rate": 10}
    ]

    """ stages = [
        {"duration": 15, "users": 3, "spawn_rate": 3},
        {"duration": 50, "users": 0, "spawn_rate": 3},
        {"duration": 60, "users": 3, "spawn_rate": 3}
    ] """

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None
