
docker-compose up
docker container prune -f

docker-compose start
docker-compose stop

### OBTAIN TOKEN TO CONNECT TO JUPYTER
docker exec -it jupyter /bin/sh
jupyter notebook list

### CONNECT TO DATABASE FROM YOUR LOCAL MACHINE
# first find ipadress to use as host
docker inspect postgres | findstr IPAddress
# the remaining info should be in the docker-compose file

### CHECK AIRLOW DAGS IN THE CONTAINER
docker exec -it airflow /bin/sh

<!-- try to parse the dag script -->
cd dags
python ~/airflow/dags/tutorial.py

<!-- list dags -->
airflow list_dags
airflow list_tasks dnbflow

<!-- test dags -->
airflow test <dag_id> <task_id> <execution_date>
airflow test dnbflow read_dnb_input 2019-11-03
airflow test dnbflow write_responses_data 2019-11-03

### DASK EXAMPLE 
```python
start1 = time.time()
df_sample['parsed_data'] = dd.from_pandas(df_sample, npartitions=4*multiprocessing.cpu_count()).\
    map_partitions(lambda df : df.apply((lambda row : newspaper_wrapper(row.url)),axis=1)).\
    compute(scheduler='processes')
end1 = time.time()
```
