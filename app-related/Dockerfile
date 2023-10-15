FROM amazonlinux:latest
RUN yum -y update
RUN yum install -y python3-pip
RUN pip3 install scikit-learn==0.24.0
RUN pip3 install pymysql
RUN pip3 install flask
RUN pip3 install boto3
COPY ./handler_diamond_price.py handler_diamond_price.py
COPY ./diamond_price_dt_model.pkl diamond_price_dt_model.pkl
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "handler_diamond_price.py" ]

