# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


#Imports that are Required for RASA to run custom Actions
from itertools import count
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted
from rasa_sdk.types import DomainDict

# Custom Action Function to Fetch and Store all the data from the slots/entities in a "rasa_data.txt" file
# This function contains all the custom logic that I have build...

file = 0     # file pointer (globally accessable) inside the custom action
class ActionOutputDatatoFile(Action):
    
    check = 1                  # Variable to manage what the Bot needs to say and ask the user.
    createNewFile = 1          # Variable to manage creation of new file each time user start a new conversation for new question
    firstTOL = ""              # Variable to save first "TOL" input by the User
    firstString = ""           # Variable to save first "String" input by the user
    ambiguousDetect = 0        # Ambiguity Check for Question
    
    def name(self) -> Text:
        return "action_fetched_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        TOA = tracker.get_slot("typeOfAutomata")          # Get the value of slot {Type of Automata} and store in variable called "TOA"
        alphabets = tracker.get_slot("alphabets")         # Get the value of slot {Alphabets} and store in variable called "alphabets"
        TOLtype = tracker.get_slot("TOL")                 # Get the value of slot {Type of Laguage} and store in variable called "TOLType"
        fetchStr = tracker.get_slot("string")             # Get the value of slot {String} and store in variable called "fetchStr"
        closure = tracker.get_slot("cloProp")             # Get the value of slot {Closure Property Type} and store in variable called "closure"
        closureYorN = tracker.get_slot("option")          # Get the value of slot {Closure? Yes / No option} and store in variable called "closureYorN"

        filePath = "C:\\Users\\Muzammil Ali\\Desktop\\RasaData\\rasa_data.txt"     # Path to file, which needs to be written
        
        # Condition to make a new file only once when this Custom Function is executed everytime
        if self.createNewFile == 1:
            file = open(filePath,"w")
            self.createNewFile = 0

        # Buttons for the User to select option for Closure -> Yes / No ?
        optionsSetButton =[
            {"title":"Yes", "payload":'/confirm_closure{"option":"Yes"}'},
            {"title":"No", "payload":'/deny_closure{"option":"No"}'}
        ]

        # Buttons for the User to select the Closure Property -> and / or 
        closureSetButton = [
            {"title":"and", "payload":'/tell_closure{"cloProp":"and"}'},
            {"title":"or", "payload":'/tell_closure{"cloProp":"or"}'}
        ]

        # Buttons for the User to select what they want to do after their recent question is finished !!
        anotherQuestionAndThankYou = [
            {"title":"Want to Solve another Question?", "payload":"/tell_have_question"},
            {"title":"No, Thank You!", "payload":"/thankyou"}
        ]

        # Buttons for User to select what to do once the Chat Bot detects Ambiguouness in the Question
        ambigQuestion = [
            {"title":"Yes", "payload":"/verify_ambiguous"},
            {"title":"No", "payload":"/neglect_ambiguous"}
        ]
        
        # condition works when check is 1 and executes what is inside and reset the check to 0
        if self.check == 1:
            
            TOA = TOA.upper()     # Converting the input to uppercase , Making sure its in Capital Letters
            TOLtype = TOLtype.lower()       # Converting the TOL to lowercase , Making sure its in small letters
            
            # What the Bot responds back to the User
            dispatcher.utter_message(text=f"Type of Automata : (**{TOA}**) ✔️\n\nAlphabets are : (**{alphabets}**) ✔️\n\nType of Language : (**{TOLtype}**) ✔️")
            dispatcher.utter_message(text=f"String : '**{fetchStr}**'✔️\n\nWould You like to add a closure property? -> (and) (or) 👇\n\n",buttons=optionsSetButton)

            # Saving the First time entered TOL and String , to check Ambiguity later...
            self.firstTOL = TOLtype
            self.firstString = fetchStr

            # Condition what to write "Type of Automata" in the "rasa_data.txt" file
            if TOA == "DFA":
                file.write("3\t\t//Type of Automata (DFA)\n")
            elif TOA == "NFA":
                file.write("2\t\t//Type of Automata (NFA)\n")
            elif TOA == "NFA-NULL":
                file.write("1\t\t//Type of Automata (NFA-NULL)\n")
            
            # Loop to write the alphabets to the file by seperating it with "," delimeter
            for data in alphabets.split(","):
                file.write(f"{data}\t\t//alphabets\n")

            # Condition what to write "Type of Language" in the "rasa_data.txt" file
            if TOLtype == "starts":
                file.write("1\t\t//starts with\n")
            elif TOLtype == "ends":
                file.write("2\t\t//ends with\n")
            elif TOLtype == "contains":
                file.write("3\t\t//contains\n")

            # Write the String to the "rasa_data.txt" file
            file.write(f"{fetchStr}\t\t//String\n")

            # Close the file which was opened in "W" -> Write Mode
            file.close()

            # Resets the check to 0 at the end of execution of this parent if statment
            self.check = 0
        
        # condition works when check is 2 and executes what is inside and reset the check to 1
        elif self.check == 2:

            TOLtype = TOLtype.lower()       # Converting the TOL to lowercase , Making sure its in small letters

            # Check for Ambiguity in the Question and updates the Ambiguity Check Variable accordingly
            if (self.firstTOL == "starts" and TOLtype == "starts") and closure == "and":
                dispatcher.utter_message(text="I have detected **Ambiguousness** in your question 🤨\n\n")
                dispatcher.utter_message(text="**Note:** Ambiguous Questions **cannot** be entertained!\n\n")
                dispatcher.utter_message(text=f"Did you just Say 👇\n\nIt (**{self.firstTOL}** with '{self.firstString}') / ***{closure}*** / (**{TOLtype}** with '{fetchStr}') ? 🤔",buttons=ambigQuestion)
                self.ambiguousDetect = 1
            elif (self.firstTOL == "ends" and TOLtype == "ends") and closure == "and":
                dispatcher.utter_message(text="I have detected **Ambiguousness** in your question 🤨\n\n")
                dispatcher.utter_message(text="**Note:** Ambiguous Questions **cannot** be entertained!\n\n")
                dispatcher.utter_message(text=f"Did you just Say 👇\n\nIt (**{self.firstTOL}** with '{self.firstString}') / ***{closure}*** / (**{TOLtype}** with '{fetchStr}') ? 🤔",buttons=ambigQuestion)
                self.ambiguousDetect = 1
           
           # Condition to Check if Ambiguity is Found in Question then Reset Slot Values and Prompt the User
           # on what to do next...
            if self.ambiguousDetect == 1:
                # Resets the new file varaible to 1 , as Ambiguity is found and the check varibale to 1 as well to start again from the top for a new question
                self.createNewFile = 1
                self.check = 1
                # The closureYorN is set to "None" so that it wont run the below conditions which are based on closureYorN
                closureYorN = "None"
                # Reset the Ambiguity Check to inital value i.e zero -> 0
                self.ambiguousDetect = 0
                
                # Resets all the Slots which were filled during the Conversation - So that same user can re-initiate a new chat
                return [SlotSet("typeOfAutomata", None), SlotSet("alphabets", None), SlotSet("option", None), SlotSet("TOL", None), SlotSet("string", None), SlotSet("cloProp", None)]               

            #### If "NO" Ambiguity is Found then Proceed to Correct Flow...Below ####

            # What the Bot responds back to the User
            dispatcher.utter_message(text=f"Closure Propery : (**{closure}**) ✔️\n\nType of Language : (**{TOLtype}**) ✔️\n\n")
            dispatcher.utter_message(text=f"String : '**{fetchStr}**' ✔️\n\nI have got the details 📝\n\n")
            dispatcher.utter_message(text=f"Click on the **Generate Solution** Button on the Webpage!\n\nIs there anything else I can help you with?",buttons=anotherQuestionAndThankYou)

            # Open the recent created file "rasa_data.txt" in "a" -> Append mode
            file = open(filePath,"a")

            # Condition what to write "Closure Property" in the "rasa_data.txt" file
            if closure == "or":
                file.write("1\t\t//(OR / Union) closure property\n")
            elif closure == "and":
                file.write("2\t\t//(AND / Intersection) closure property\n")
            
            # Condition what to write "Type of Language" in the "rasa_data.txt" file (Second Round - Last Round)
            if TOLtype == "starts":
                file.write("1\t\t//starts with\n")
            elif TOLtype == "ends":
                file.write("2\t\t//ends with\n")
            elif TOLtype == "contains":
                file.write("3\t\t//contains\n")

            # Write the String to the "rasa_data.txt" file
            file.write(f"{fetchStr}\t\t//String\n")

            # Close the file which was opened in "A" -> Append Mode
            file.close()
            
            # Resets the new file varaible to 1 , as the question has ended + Resets the check varibale to 1 as well to start again from the top for a new question
            self.createNewFile = 1
            self.check = 1
            # The closureYorN is set to "None" so that it wont run the below conditions which are based on closureYorN
            closureYorN = "None"
            
            # Resets all the Slots which were filled during the Conversation - So that same user can re-initiate a new chat
            return [SlotSet("typeOfAutomata", None), SlotSet("alphabets", None), SlotSet("option", None), SlotSet("TOL", None), SlotSet("string", None), SlotSet("cloProp", None)]

        # Condtion to check the value of "closureYorN" and execute accordingly
        if (closureYorN == "yes" or closureYorN == "Yes" or closureYorN == "Y" or closureYorN == "y") and self.check != 2:
            
            # What the Bot responds back to the User
            dispatcher.utter_message(text=f"**Closure Property**\n\nClick on your choice below 👇",buttons=closureSetButton)
            
            # Set the value of the check variable to 2
            self.check = self.check + 2
            
            # Reset the "String" slot to "None" so that the user can enter the string again for last-round input because they selected Want Closure? as Yes
            return [SlotSet("string", None)]
        
        elif closureYorN == "no" or closureYorN == "No" or closureYorN == "N" or closureYorN == "n":
            
            # What the Bot responds back to the User
            dispatcher.utter_message(text=f"I have got the details 📝\n\n")
            dispatcher.utter_message(text=f"Click on the **Generate Solution** Button on the Webpage!\n\nIs there anything else I can help you with?",buttons=anotherQuestionAndThankYou)

            # Open the recent created file "rasa_data.txt" in "a" -> Append mode
            file = open(filePath,"a")

            # Write the "0" to the "rasa_data.txt" file as the User select Want Closure? to "No" therfore the question ends here
            file.write("0\t\t//(NONE) closure property\n")

            # Close the file which was opened in "A" -> Append Mode
            file.close()

            # Resets the new file varaible to 1 , as the question has ended + Resets the check varibale to 1 as well to start again from the top for a new question
            self.createNewFile = 1
            self.check = 1
            
            # Resets all the Slots which were filled during the Conversation - So that same user can re-initiate a new chat
            return [SlotSet("typeOfAutomata", None), SlotSet("alphabets", None), SlotSet("option", None), SlotSet("TOL", None), SlotSet("string", None), SlotSet("cloProp", None)]

        # return nothing , slots are unchanged.
        return []

# String Validation Function that runs on realtime when the Bot prompts you to " enter the string "
class ValidateStringForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_string_form"

    def validate_string(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        alphabets = tracker.get_slot("alphabets")   # get the alhabets with  "," separation exp , (a,b)
        eachAlphabetList = alphabets.split(",")     # split the alphbets and make a list exp , ["a","b"]
        string = slot_value                         # get the input string from the user exp , aaabbaba or 1100101 etc
        stringUniqueList = set(string)              # get the Distinct List from the string input exp , ["a","b"] or ["0","1"]
        check = 0                                   # check for ALphabets and Unique List on string comparison

        # Debuggin for my self -> will print data in the "rasa run actions" console
        print("Alphabets : ",eachAlphabetList)
        print("\nString : ",string)
        print("\nString Distinct List : ",stringUniqueList)
        print("\n")

        # Loop to iterate each element between the Distinch List of characters in the "Entered String"
        for alphabet in stringUniqueList:
            
            # Check if the iterated element is present in the "Alphabets" list or no , which was enter by the User in the start example (a,b)
            if alphabet in eachAlphabetList:
                # If string character is from the alphabet list..... proceed further and set that string as slot value of "String"
                check = 1
            else:
                # If the string character is not present in the alphabet list .... prompt an Error to the user and ask them to re-enter the correct string
                check = 2
                # break the loop even one of the string distinct character does't match
                break
        # The string characters are Valid!
        if check == 1:
            # The Entered String is Valid therefore set it to the "String" slot/entity
            return {"string": slot_value}
        
        # The string characters are Invalid!
        else:
            # Bot prompts the User with an Error
            dispatcher.utter_message(text=f"The entered string is Invalid ❌\n\nPlease re-enter the string...")
            
            # The Entered String is Invalid therefore set the Slot "String" to None and Re-Ask the User to enter the correct string
            return {"string": None}

# Alphabets Validation Function that runs on realtime when the Bot prompts you to " enter the alphabets "
class ValidateAlphabetsForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_alphabets_form"

    def validate_alphabets(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        alphaInput = slot_value             # Storing Alphabet Input from the fetched Slot "alphabets"
        alphabetCheck = 0                   # Check for Alphabets Format on the left and right of "," comma
        commaCheck = 0                      # Check that Alphabet Input contain "," comma in the center

        # Printed on the Console for debugging
        print(f"The Alphabet Slot Value I got is : {alphaInput}\n")

        # Condition to check if the Alphabet Input length is Valid or No
        if len(alphaInput) > 3 or len(alphaInput) < 3:
            # What the Bot prompts back to User
            dispatcher.utter_message(text="Invalid Input ❌")
            # The Entered Alphabets is Invalid therefore set the Slot "alphabets" to None and Re-Ask the User to enter the correct alphabets
            return {"alphabets": None}
        # If the Length Check is Valid then proceed to this condition
        else:
            # Converting the written input to lowercase
            alphaInput = alphaInput.lower()
            
            # Validating that left side of "," is alphabet/numeric AND right side of "," is also either alphabet/numeric
            if ((alphaInput[0] >= 'a' and alphaInput[0] <= 'z') or (alphaInput[0] >= '0' and alphaInput[0] <= '9')) and ((alphaInput[2] >= 'a' and alphaInput[2] <= 'z') or (alphaInput[2] >= '0' and alphaInput[2] <= '9')):
                # Check Updated that Alphabet/numeric format is "Correct"
                alphabetCheck = 1
        
        # Validating that the center input is a "," for sure
        if alphaInput[1] == ',':
            # Check Updated that "," is in the right place, "Correct" format
            commaCheck = 1

        # If both the Alpbaet/Numeric Input + the "," is correct , In-Short it is a Valid "alphabets" Input
        if alphabetCheck == 1 and commaCheck == 1:
            
            # Validation if the Alphabets on the left and right are same , incase
            if alphaInput[0] == alphaInput[2]:
                dispatcher.utter_message(text="Alphabets cannot be Same ❌")
                return {"alphabets": None}
            else:
                # Console Output -> Success
                print("\nAlphabet input is (Valid...)")
                # The Entered Alphabet is Valid therefore set it to the "alphabets" slot/entity
                return {"alphabets": slot_value}
        else:
            # Bot Prompts with the Error to Re-Enter Input
            dispatcher.utter_message(text="Invalid Input ❌\n\nKindly follow the format ...")
            # The Entered Alphabet is Invalid therefore set the Slot "alphabets" to None and Re-Ask the User to enter the correct alphabets
            return {"alphabets": None}