Gmail Invoice Exporter
======================

## Introduction
Using this repository you can extract invoices from your Gmail account as PDF files and sort them based on their dates.
It is useful when you want to submit your expenses to your accountant/tax authorities for VAT declaration.

There are two types of invoices that I usually get:
1. A PDF file that is attached to the email
2. An HTML based invoice which is the body of the email itself

Second part was a bit tricky to convert to PDF, since there are no pure Python implementations to convert text to pdf in a
pretty format I used `libreoffice` which is install in the Docker image we are using.



## How to use

1. You need to [enable](https://support.google.com/googleapi/answer/6158841?hl=en) your **Gmail API**.
2. Then you need to [create a credentials](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) 
file as a JSON and put it under `config` directory. 
3. Now you need to make sure you [create filters](https://support.google.com/mail/answer/6579?hl=en#zippy=%2Ccreate-a-filter) for emails that you want to extract invoices for to apply appropriate labels. 
While creating these filters you can use `from` keyword or `has the words` and in the end make sure to apply a new label for this filter. 
You can test your filter by clicking on the label that you created under Labels in your Gmail UI. 
4. Now modify `config/data.json` to include the labels you want. Indicate the type of the invoice for each label. You need 
to also indicate the time period you want to fetch these invoices.
5. Run `docker-compose up`
6. This will generate a URL for you to do OAUTH step for your Gmail account. Authorize the application and let the script
do its job. 
7. You will have all the invoices stored under `/data` directory. 