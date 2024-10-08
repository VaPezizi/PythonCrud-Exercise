import azure.functions as func
import logging
import pyodbc 

#Huom, Ohjelma sisältää vielä paljon ongelmia ja on vähän huonosti tehty aika paineen vuoksi.
#Kaiken pitäisi toimia kumminkin.
#Tiedon päivitys tapahtuu sähköposti osoitteen mukaan, toisin kuin tiedon poisto ja haku, jotka toimivat ID:llä

#CURL KOMENNOT

#All of the links are changed from the original

#curl -X PUT "https://tietokanta.azurewebsites.net/api/customer?EmailAddress=jari@sposti.fi&MiddleName=Moro"
#curl -X POST "https://tietokanta.azurewebsites.net/api/customer?CompanyName=firma&EmailAddress=sami@sposti.fi&FirstName=Jari&LastName=jaarii&MiddleName=J&Suffix=Mr&PasswordHash=1234&PasswordSalt=12345&Phone=033123&SalesPerson=Jake&Title=Voittaja"
#curl https://tietokanta.azurewebsites.net/api/customer?id=5
#curl -X DELETE https://tietokanta.azurewebsites.net/api/customer?id=5

# Azure SQL Database connection parameters
server = 'tcp:tietokanta.database.windows.net'
database = 'tietokanta'
username = 'USER'
password = 'PASSWORD'
driver = '{ODBC Driver 18 for SQL Server}'

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="customer", auth_level=func.AuthLevel.ANONYMOUS)
def get_customer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing HTTP request to fetch customer by ID.')

    # Get the customer ID from the query parameters
    #customer_id = req.params.get('id')

    try:
        # Connect to Azure SQL Database
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        cursor = conn.cursor()
        

        if(req.method == "POST"):
            CompName = req.params.get('CompanyName')
            Email = req.params.get('EmailAddress')
            FirstName = req.params.get('FirstName')
            LastName = req.params.get('LastName')
            MiddleName = req.params.get('MiddleName')
            Suffix = req.params.get('Suffix')
            PasswordHash = req.params.get('PasswordHash')
            PasswordSalt = req.params.get('PasswordSalt')
            Phone = req.params.get('Phone')
            #NEWID()
            SalesPerson = req.params.get('SalesPerson')
            Title = req.params.get('Title')

            #string = FirstName

            #(CompanyName, EmailAddress, FirstName, LastName, MiddleName, ModifiedDate, NameStyle, PasswordHash, PasswordSalt, Phone, rowguid, SalesPerson, Suffix, Title)
            sql = f"INSERT INTO SalesLT.Customer (CompanyName, EmailAddress, FirstName, LastName, MiddleName, ModifiedDate, NameStyle, PasswordHash, PasswordSalt, Phone, rowguid, SalesPerson, Suffix, Title) VALUES(?, ?, ?, ?, ?,GETDATE(),0,?,?,?, NEWID(), ?, ?, ?)"
            
            params = (CompName, Email, FirstName, LastName,MiddleName,PasswordHash, PasswordSalt, Phone, SalesPerson, Suffix, Title)
            cursor.execute(sql, params)
            cursor.commit()
            return func.HttpResponse(f"{req.method}")

        if(req.method == "PUT"):
            
            #I know it's probably stupid, but i'm WAY too tired to come up with a better way at this time
            
            parameters = []
            updates = []

            CompName = req.params.get('CompanyName')
            Email = req.params.get('EmailAddress')
            FirstName = req.params.get('FirstName')
            LastName = req.params.get('LastName')
            MiddleName = req.params.get('MiddleName')
            Suffix = req.params.get('Suffix')
            Phone = req.params.get('Phone')
            Title = req.params.get('Title')

            if not Email:
                return func.HttpResponse("Email required for updating data!")

            if (CompName):
                parameters.append(CompName)
                updates.append("CompanyName = ?")
         
            if (FirstName):
                parameters.append(FirstName)
                updates.append("FirstName = ?")
            if (LastName):
                updates.append("LastName = ?")
                parameters.append(LastName)
            if(MiddleName):
                updates.append("MiddleName = ?")
                parameters.append(MiddleName)
            if(Suffix):
                updates.append("Suffix = ?")
                parameters.append(Suffix)
            if(Phone):
                updates.append("Phone = ?")
                parameters.append(Phone)
            if(Title):
                updates.append("Title = ?")
                parameters.append(Title)

            if(not updates):
                return func.HttpResponse("No fields found to update", status_code=400)

            #NOTE: I know it's very ugly :D

            sql=f"UPDATE SalesLT.Customer SET {', '.join(updates)} WHERE EmailAddress = ?"
            parameters.append(Email)
            #param = tuple(parameters)
            #for item in lista:
            #   if item!='':
            #        QueryString+=f' {strLista[i]} = {item}'
            #    i=i+1
            #(CompanyName, EmailAddress, FirstName, LastName, MiddleName, ModifiedDate, NameStyle, PasswordHash, PasswordSalt, Phone, rowguid, SalesPerson, Suffix, Title)
            #sql = f"UPDATE SalesLT.Customer SET {}"
            cursor.execute(sql, parameters)
            cursor.commit()
            return func.HttpResponse(f"Succesfully updated info for {Email}!")
            #return func.HttpResponse(f"{sql} ||| {parameters}")


        customer_id = req.params.get('id')      ##GETTING THE ID HERE!!

        if not customer_id:
            return func.HttpResponse(
                "Please provide a customer ID in the query string.",
                status_code=400
            )

        # Query the customer table by ID

    #except pyodbc.Error as e:
     #   logging.error(f"Database error: {str(e)}")
      #  return func.HttpResponse(f"Error connecting to the database: {str(e)}", status_code=500)
        #return func.HttpResponse(f"{req.method, customer_id}")

        

        if(req.method == "DELETE"):
            string = f"DELETE FROM SalesLT.Customer WHERE CustomerID = {customer_id}"
            cursor.execute(string)
            cursor.commit()
            return func.HttpResponse(f"{string,req.method, customer_id}")        


        if(req.method == "GET"):
            cursor.execute("SELECT * FROM SalesLT.Customer WHERE CustomerID = ?", customer_id)
            row = cursor.fetchone()

            if row:
                # Format the customer data as a string or JSON
                customer_data = {
                    "CustomerID": row[0],
                    "CustomerName": row[1],
                    "ContactName": row[2],
                    "Country": row[3]
                }
                return func.HttpResponse(f"Customer Details: {customer_data}", status_code=200)
            else:
                return func.HttpResponse(f"No customer found with ID {customer_id}.", status_code=404)

    except pyodbc.Error as e:
        logging.error(f"Database error: {str(e)}")
        return func.HttpResponse(f"Error connecting to the database: {str(e)}", status_code=500)

    finally:
        # Close the database connection
        cursor.close()
        conn.close()
