import docker, os, time, logging, json
import schedule
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
def build_env(base_path, files):
        if files:
                env = {}
                for file in files:
                        env.update(dotenv_values(os.path.join(base_path, file)))
                return env
        else:
                return {}

with open(os.path.join(compose_dir,"docker-compose.yml"), 'r') as f2:
        data = load(f2, Loader=Loader)
        for service in data['services']:
                services[app_name+"_"+service] = build_env(compose_dir, data['services'][service].get('env_file', None))

def job(image):
        for service, env in services.items():
                if service == app_name+"_"+image:
                        logging.info("running container "+ image)
                        logging.debug("%s %s_default" % (service, app_name))
                        container = client.containers.run(service, environment=env, network=app_name+"_default", name=app_name+"_"+image)
                        return
def load_sched():
        schedule.clear()
        with open(os.path.join(compose_dir, "job_schedule.json")) as f:
                sched = json.load(f)
                for jobname, s in sched['jobs'].items():
                        j = schedule.every(s['interval'])
                        j = getattr(j, s['unit'])
                        j.do(job, jobname)

load_sched()
logging.info("Scheduler running")
logging.info(str(schedule.jobs))
while True:
    schedule.run_pending()
    time.sleep(1)
