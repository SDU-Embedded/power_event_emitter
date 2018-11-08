FROM leonbondelarsen/sdu_gstreamer
RUN cd /gst-build/subprojects/gst-plugins-bad/ && \
  git checkout leon_new_plugin && \
  cd /gst-build && \
  ninja -C build/ install
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  kafkacat
COPY files/ /
RUN rm -r /gst-build
CMD ["/scripts/do_run"]

