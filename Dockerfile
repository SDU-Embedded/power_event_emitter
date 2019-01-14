FROM leonbondelarsen/sdu_gstreamer
RUN cd /gst-build/subprojects/gst-plugins-bad/ && \
  git fetch && \
  git checkout leon_new_plugin && \
  cd /gst-build && \
  ninja -C build/ install
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  kafkacat 
RUN pip3 install --upgrade pip 
RUN pip3 install kafka-python

COPY files/ /
RUN rm -r /gst-build
CMD ["/scripts/do_run"]

