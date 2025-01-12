import requests
import logging

# Configure logging
logging.basicConfig(
    filename="implementation_to_awaiting_wo_update.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Endpoint
url_template = "https://***.robi.com.bd/api/***/update-workorder/{}"

# Headers and data
headers = {
    "X-Auth-Token": "***2Zv1K6CjI8qk1PUjvw5GBlkLVz6gsw3xKi1QtgwpYXGLo1Gz5Y9Ucl***"
}
data = {
    "approvalStatus": "1",
    "planningRemarks": "Bypassing Planning Approval"
}

# List of IDs
ids = [49482, 49470, 49465, 49463, 49462, 49461, 49460, 49459, 49458, 49457, 49456, 49454, 49435, 49434, 49431, 49430, 49429, 49427, 49425, 49424, 49423, 49422, 49421, 49420, 49419, 49418, 49417, 49416, 49415, 49409, 49405, 49404, 49403, 49402, 49401, 49399, 49398, 49396, 49395, 49394, 49393, 49392, 49391, 49390, 49389, 49387, 49383, 49372, 49365, 49319, 49289, 49256, 49236, 49176, 49104, 48976, 48964, 48099, 48092, 47934, 47875, 47126, 46939, 46825, 46740, 46589, 45733, 45679, 45678, 45594, 44527, 44180, 43756, 43400, 42557, 41363, 40512, 37241, 34768]

# Function to call the API for each ID
def update_workorder(ids):
    logging.info("Starting workorder update process")
    for workorder_id in ids:
        url = url_template.format(workorder_id)
        logging.info(f"Processing WorkOrder ID: {workorder_id}")
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                logging.info(f"Success: WorkOrder ID {workorder_id}")
                print(f"Success: WorkOrder ID {workorder_id}")
            else:
                logging.error(f"Failed: WorkOrder ID {workorder_id} - Status Code {response.status_code}")
                print(f"Failed: WorkOrder ID {workorder_id} - Status Code {response.status_code}")
        except Exception as e:
            logging.error(f"Error: WorkOrder ID {workorder_id} - {e}")
            print(f"Error: WorkOrder ID {workorder_id} - {e}")
    logging.info("Workorder update process completed")

# Call the function
update_workorder(ids)
