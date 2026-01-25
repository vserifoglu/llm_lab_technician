I want you to act as a senior Data engineer at google. I also want you to be expert at exocad teeth design program. I attached an image of the files i have for a patient case. 


I wanna understand the data and what it contains. I will share with you the workflow the designer go through from the scan to the actual manufacturing of the new tooth.  


Here is the workflow: 


- dentist send a copy of the patient teeth. 

- lab technician using a scanner, scans the copy and saves a digital version of it. 

- then opens it using exocad to start working on it. 

- then draw the margin line for every single tooth, the margin line is the edge between the gum and the new tooth. 

- Then it install the needed tooth library which gives a digital tooth for the one they are working on. 

- then they place it in the gab and fix its dimensions. 

- then they hit save and send it to the mine machine to manufacture it. 


Going through this process is tidious and requires multiple routine steps from the lab designer. And if you wanna increase productivity, you have to get more designers to the lab. Therefore, I aim to automate this process or part of it, so the productivity can increase while the number of designers remain the same or less. 


To automate this, we cannot include all the steps of the process from the get-go. We have to choose the most boring and most time consuming step and automate it, then test it in production, then get feedback, then enhance the automation too to include more feature and more steps. At the end, the objective goal is to automate the entire process gradually. 


To start gradually, I am going to start with the margin lines between the gum and the new tooth. Imagine a patient with 10-15 teeth to replace? In this case it will take the designer around 10-15 minutes to draw only the margin lines for the teeth. Automating this step will save 15 minutes per case, increasing the number of cases done per day. Therefore, instead of taking 40 minuts to finalize the case, it will take 25 minutes and so on and so forth. 


The solution for automating this step will be using AI for sure. We will train a deep learning model to detect the margin lines given that some cases don't have clear shoulders since we are dealing with variant doctors whom don't have the exact quality among each other. But we will think about this later. More importantly is the data, and how we are going to engineer thhe data to feed the mode. 


The data is the most important step for me at the moment, I have attached an image of a single tooth case which contains all the finalized design files. In order to automate the margin, we must do the following: 


- first need to figure out what the margins are for this case 

- verify that these margins are correctly been saved. 

- be 100% sure of the fields where these margins are being stored so that when we scale to 500 GB of data, we will be sure of what we are working on. 


To give you an overview of the data: 

- we have multiple stl files 

- we have multiple xml files which contains the margins i believe; i will share an example below 

<MarginBottomType>CrownBottom</MarginBottomType>

      <AxisInsertionScanInfo>

        <x>0.10854307562112808</x>

        <y>-0.014182517305016518</y>

        <z>-0.9939906001091003</z>

      </AxisInsertionScanInfo>

      <AxisInsertionWasCheckedOrDefined>true</AxisInsertionWasCheckedOrDefined>

      <Axis>

        <x>1.3877787807814457E-17</x>

        <y>0</y>

        <z>1.0000000280838248</z>

      </Axis>

      <AxisOcclusalOfToothModel>

        <x>-0.06562006923997077</x>

        <y>-0.057317789216587214</y>

        <z>0.9961971077815195</z>

      </AxisOcclusalOfToothModel>

      <AxisMesial>

        <x>-0.9835750417393003</x>

        <y>0.17197499408373262</y>

        <z>-0.0548154966905675</z>

      </AxisMesial>

      <AxisBuccal>

        <x>0.16817908656308975</x>

        <y>0.9834316122045478</y>

        <z>0.06766135499358933</z>

      </AxisBuccal>



My current objective is to:


- to know which files I need for training the AI model.  

- to know which specific data i need from the files. 


If you have any questions, ask!

if you want more information, ask!

if you are not sure of something, don't assume, But ask!