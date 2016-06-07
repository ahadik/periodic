module.exports = (function(){
	var container process.env.CONTAINER || "test";
	var vcap = {
		services:{
		    "user-provided": [
		        {
		        	"name": "node-file-upload-sl-os-store",
		        	"label": "user-provided",
		        	"credentials": {
		        		"auth_url": 'https://dal05.objectstorage.softlayer.net/auth/v1.0/',
		        		"userId": 'SLOS925675-4:SL925675',
		        		"password": 'df5a1a79d01be2ec263835f93ad02a88b67af6aa3f30c6a89f88a81bddc3cc86',
		        		"container": container
		        	}
		        }
		    ]
		}
	}
	return vcap;
})();