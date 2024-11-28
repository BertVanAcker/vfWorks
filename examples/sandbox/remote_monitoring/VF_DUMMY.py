# telegraph.py - Retrieves data from Redis when new data is added
import redis

def VF_M1(verbose=False):
    # Connect to Redis server
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Subscribe to the data channel to get notified of new data
    pubsub = r.pubsub()
    pubsub.subscribe('MONITOR_NEW_DATA')
    print("Telegraph: Subscribed to data channel")

    # Listen for new messages on the channel
    for message in pubsub.listen():
        if message['type'] == 'message':
            if verbose:print(message['data'])


            if "poi1" in message['data'].decode('utf-8'):
                if verbose:print("Monitoring POI1...")
                data = r.get('VF_M1:properties:poi1').decode('utf-8')
                if verbose: print(data)
                # RANGE CHECK
                if 0 <= float(data) <= 100:
                    if verbose:print("POI1 is VALID")
                    r.set('VF_M1:specifications:SPECIFICATION1',"VALID")
                else:
                    print("POI1 is INVALID")
                    if verbose:r.set('VF_M1:specifications:SPECIFICATION1', "INVALID")
            elif 'poi2' in message['data'].decode('utf-8'):
                if verbose:print("Monitoring POI2...")
                data = r.get('VF_M1:properties:poi2').decode('utf-8')
                if verbose: print(data)
                # RANGE CHECK
                if 0 <= float(data) <= 2:
                    if verbose:print("POI2 is VALID")
                    r.set('VF_M1:specifications:SPECIFICATION2', "VALID")
                else:
                    if verbose:print("POI2 is INVALID")
                    r.set('VF_M1:specifications:SPECIFICATION2', "INVALID")
            elif "poi3" in message['data'].decode('utf-8'):
                if verbose:print("Monitoring POI3...")
                data = r.get('VF_M1:properties:poi3').decode('utf-8')
                if verbose: print(data)
                # RANGE CHECK
                if 0 <= float(data) <= 10000:
                    if verbose:print("POI3 is VALID")
                    r.set('VF_M1:specifications:SPECIFICATION3', "VALID")
                else:
                    if verbose:print("POI3 is INVALID")
                    r.set('VF_M1:specifications:SPECIFICATION3', "INVALID")


if __name__ == "__main__":
    VF_M1(verbose=True)
