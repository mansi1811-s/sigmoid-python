from flask import Flask
from flask import render_template,request

import boto3
import botocore
from botocore.exceptions import ClientError



client = boto3.client('s3')

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

#List S3 buckets
@app.route('/listing')
def listing():
   # client = boto3.client('s3')
    list_buckets=client.list_buckets()
    buckets=list_buckets["Buckets"]
    #print(buckets)
    return render_template('result.html',buckets=buckets)

# Create a new S3 bucket 
@app.route('/create_bucket', methods=['POST']) 
def create_bucket():
   bucket_name = request.form['bucket_name'] 
   try:
       client.create_bucket(Bucket=bucket_name,
                            CreateBucketConfiguration={
             'LocationConstraint': 'ap-south-1' }
                            ) 
   except client.exceptions.BucketAlreadyExists:
      print(f"s3 bucket{bucket_name} already exists")
   except client.exceptions.BucketAlreadyOwnedByYou:
      print(f"S3 bucket {bucket_name} already owned by you")
   except botocore.exceptions.ClientError as e:
      print(e)
   return render_template('status.html', message='Bucket created successfully')


#Upload file to s3 bucket
@app.route('/upload_file', methods=['POST'])
def upload_file():
   
   bucket_name=request.form['bucket_name']
   try:
      file=request.files['file']
      file_name=file.filename
      client.upload_fileobj(file, bucket_name,file_name)
   except botocore.exceptions.ClientError as error:
      return render_template('status.html',message=error)

   return render_template('status.html',message='File uploaded successfully')




#Create folder inside a bucket
@app.route('/create_folder' , methods=['POST'])
def create_folder():
   try:
      bucket_name = request.form['bucket_name']
      directory_name = request.form['directory_name']
      client.put_object(Bucket=bucket_name, Key=(directory_name+'/'))
      return render_template('status.html',message='Folder created succesfully')
   except ClientError as e:
       message= e.response["Error"]['Code']
       return render_template('status.html',message=message)



#Delete S3 bucket
@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
   del_buck=request.form['del_buck']
    
   try:
      result = client.list_objects_v2(Bucket=del_buck)
   except botocore.exceptions.ClientError as e:
       raise e

   finally:
      if 'Contents' in result:
         del_all_obj(del_buck)
      else:
         response = client.delete_bucket(
      Bucket=del_buck   
         )
   return render_template('status.html',message='Bucket deleted succesfully')



#Delete objects
def del_all_obj(del_buck):
    
        response=client.list_objects_v2(Bucket=del_buck)
        files=response["Contents"]
        files_del=[]
    # print(response)
        for f in files:
            files_del.append({"Key": f["Key"]})

        if "Contents" in response:
            response=client.delete_objects(
            Bucket=del_buck,
            Delete={"Objects" : files_del}
            )

        response = client.delete_bucket(Bucket=del_buck  )
        

#Delete files in a bucket
@app.route('/del_file',methods=['POST'])
def del_file():
      bucket_name=request.form['bucket_name']
      file_name=request.form['file_name']
      response = client.delete_objects(
      Bucket=bucket_name,
      Delete={
         'Objects': [
               {'Key': file_name},
                     ],
               },
                                       )
      return render_template('status.html',message="File deleted succesfully")






#Copy files from one bucket to another
@app.route('/copy',methods=['POST'])
def copy():
    src_bucket=request.form['src_bucket']
    src_file=request.form['src_file']
    des_bucket=request.form['des_bucket']
    des_file=request.form['des_file']

    copy_source = {
         'Bucket': src_bucket, 
         'Key': src_file
    }
    response = client.copy_object(
        Bucket=des_bucket,
        CopySource=copy_source,
        Key=des_file   
    )
    return render_template('status.html',message="Object copied")


#Move files within S3 bucket
@app.route('/move',methods=['POST'])
def move():
   src_bucket=request.form['src_bucket']
   src_file=request.form['src_file']
   des_bucket=request.form['des_bucket']
   des_file=request.form['des_file']
   copy_source = {
         'Bucket': src_bucket, 
         'Key': src_file
    }
   response = client.copy_object(
        Bucket=des_bucket,
        CopySource=copy_source,
        Key=des_file     
    )
   client.delete_object(Bucket=src_bucket,Key=src_file)
   return render_template('status.html',message="Object moved successfully")


#List objects
@app.route('/get_Objects',methods=['POST'])
def get_Objects():
   bucket_name=request.form['bucket_name']
   s3 = boto3.resource('s3')

   my_bucket = s3.Bucket(bucket_name)
   obj=[]

   for my_bucket_object in my_bucket.objects.all():
       obj.append(my_bucket_object.key)
   
   return render_template('objlist.html',obj=obj)


