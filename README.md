# homeclimate

Scripts and files for the homeclimate project on [my homepage](https://nicokrieger.de/homeclimate_v1.html).
`scripts` contains the python code to pull metrics from a variety of sensors and send it to an InfluxDB database. 
`services` are the systemd unit files to execute the scripts after boot and keep them running in case they crash.
`statistics` contains some early examples of analysis plots generated with `scripts/homeclimate_statistics`. The statistics stuff does not run as a service and I did not continue to develop it. Instead, just plot the intereting stuff in a Jupyter notebook.
