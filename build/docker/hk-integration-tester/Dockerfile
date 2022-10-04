FROM public.ecr.aws/lambda/python:3.8

WORKDIR ${LAMBDA_TASK_ROOT}
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

COPY assets/ .

RUN pip3 install -r ./application/hk/integration/requirements.txt --target "${LAMBDA_TASK_ROOT}"
RUN pip3 install pytest

EXPOSE 8080

CMD [ "application.hk.integration.handler.request" ]

# FROM python:3

# WORKDIR /usr/src/app

# COPY assets/hk/integration/requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY assets/ .

# CMD [ "python", "./handler.py" ]
