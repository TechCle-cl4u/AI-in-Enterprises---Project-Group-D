# AI-in-Enterprises---Project-Group-D
This repository is for the group project of group D for the course "AI in Enterprises".

The project is on a tool that can be used in the HR department to automatically scan CV's of up to 5 applicants and comparing them with the job description.
The LLM gives a recommendation, combined with reasons, for the applicants. In addition, if the job description is not fully given yet, one can generate a job description based on an input text.

## Original Job Description
<img width="1066" height="416" alt="Bildschirmfoto 2026-01-03 um 22 57 03" src="https://github.com/user-attachments/assets/d9e0946a-707c-4afe-af55-4a4c8866d077" />
If one already has a job description, the user can insert it and use it without optimizing it using a LLM.

## Optimized Job Description
<img width="1051" height="412" alt="Bildschirmfoto 2026-01-03 um 22 58 32" src="https://github.com/user-attachments/assets/902f53e7-4745-4e9a-b0c3-4f5b2d34559b" />
If one does not have a job description yet, one can add notes to what the position requires. These notes can be used to generate a more detailed job description including the skills the position. 

## Upload of up to 5 CV's
<img width="1466" height="808" alt="Bildschirmfoto 2026-01-03 um 23 01 15" src="https://github.com/user-attachments/assets/52511634-397b-4eb1-afb8-49a86957aa80" />
The application checks the amount of files uploaded. If the total amount is above 5 it will give an alert. In addition, it will show which of these 5 CV's will be processed

## Screening of CV's + Recommendation
<img width="616" height="509" alt="Bildschirmfoto 2026-01-03 um 23 01 34" src="https://github.com/user-attachments/assets/3fba896d-d487-4c3b-9377-2ef80fb973c6" />
If the job description is uploaded, the CV's are given, and the execution button is hit, the screening of CV's will start. 

## Adaption of prompt
There is an extra page, that can be accessed using the navigation on the sidebar, allowing to adapt the prompt used for ranking the CV's. Some parts of the prompt are given, some can be adapted by the user. A preview of the complete prompt will be shown.

## Log File Analysis
Every execution is logged by the system. The log file includes a run ID, the prompt, result, duration, feedback and model used. This is the basis for visuals such as the user satisfaction, average duration per model.

# Run Application
Install required packages by typing **pip install requirements** in the Terminal

After downloading start the app by running **"streamlit run app.py"** in Terminal to test application. 

Ensure that terminal is opened in correct folder and the Ollama models are running in the background. 

The available models can are shown on the sidebar of the streamlit app.

## Usage of cloud model
In order to use cloud model save your api key in api_key.txt.
