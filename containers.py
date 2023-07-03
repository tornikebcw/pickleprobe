import docker


def is_container_running(container_name: str) -> Optional[bool]:
    RUNNING == "running"
    docker_client = docker.from_env()
    try:
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == RUNNING
