# Instructions to run event emitter on swarm


# Setup cofig (exmaple config in config/power_event_emitter_config)
docker config create cage1_power_event_emitter_config cage1_power_event_emitter_config

# Start service
docker service create --name cage1_power_event_emitter --config cage1_power_event_emitter_config --network="host" leonbondelarsen/sdu_gstreamer_event_emitters


