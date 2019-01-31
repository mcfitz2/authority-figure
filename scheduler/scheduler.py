import docker, os, time, logging, json
import schedule, pprint
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
from dotenv import dotenv_values

compose_dir = "/compose"
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


client = docker.DockerClient(base_url='unix://var/run/docker.sock')
services = {}
app_name = os.environ['COMPOSE_NAME']

def job(image, env):
        logging.info("running container "+ image)
        try:
                existing = client.containers.get(app_name+"_"+image.split(":")[1])
                logging.info("container exists with status: %s" % existing.status)
                if existing.status == "running":
                        logging.info("container is running. skipping...")
                        return
                else:
                       logging.info("container is stopped, removing and recreating...")
                       existing.remove()
        except docker.errors.NotFound:
                pass
        container = client.containers.run(image, detach=True,environment=dotenv_values(os.path.join(compose_dir, env)), network=app_name+"_default", name=app_name+"_"+image.split(":")[1])
def load_sched():
        schedule.clear()
        with open(os.path.join(compose_dir, "job_schedule.json")) as f:
                sched = json.load(f)
                for jobname, s in sched['jobs'].items():
                        j = schedule.every(s['interval'])
                        j = getattr(j, s['unit'])
                        j.do(job, jobname, s['env'])

load_sched()
logging.info("Scheduler running")
logging.info(str(schedule.jobs))
while True:
    schedule.run_pending()
    time.sleep(1)
