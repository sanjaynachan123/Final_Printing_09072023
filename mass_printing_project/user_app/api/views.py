from io import BytesIO
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user_app.models import File
from user_app.api.serializers import RegistrationSerializer,FileSerializer,ExtractedDataSerializer,ExtractAdvisorSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveUpdateDestroyAPIView)
from rest_framework.viewsets import ModelViewSet
from PyPDF2 import  PdfReader
from rest_framework.views import APIView
from user_app.models import ExtractedData,ExtractedAdvisor
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.core.files.base import ContentFile
from rest_framework.parsers import MultiPartParser




 
@api_view(['POST'])
def register_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        
        data = {}
        if serializer.is_valid():
            user_obj = serializer.save()
            data['username'] = user_obj.username
            data['email'] = user_obj.email
            data['response'] = 'Registration successful'

            token = Token.objects.get(user=user_obj).key
            data['token'] = token

        else:
            data = serializer.errors

        return Response(data,status=status.HTTP_201_CREATED)


@api_view(['POST',])
def logout_view(request):
    if request.method == 'POST':
        print(f'user is {request.user}')
        if request.user.is_anonymous:
            print(f'anonymous user')
            return Response({'error':'No credentials found'},status=status.HTTP_401_UNAUTHORIZED)

        request.user.auth_token.delete()
        return Response({'success':'You have successfully logged out'},status=status.HTTP_200_OK)



class AllFileView(ListAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class AllFileByUserView(ListAPIView):
    '''only user himself can access his files'''
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return File.objects.filter(uploader=user.id)


class FileDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return File.objects.all()
        else:
            return File.objects.filter(uploader=user.id)


class FileCreateView(CreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(uploader=user)
        

 

class ExtractedAdvisorView(APIView):
    parser_classes = [MultiPartParser]
    def post(self,request):
        pdf_file = request.FILES.get('pdf_file')
        print(pdf_file)
        extracted_advisors_list = self.extract_advisor_data(pdf_file)
        # print('returned extracted_advisors_list ',extracted_advisors_list)
        extracted_advisors_objects = []
        for advisor in extracted_advisors_list:
            if 'name' in advisor and 'address' in advisor and 'occupation' in advisor and 'home_phone' in advisor and 'account_owner' in advisor:
             advisor_pdf = self.generate_advisor_pdf(advisor)
             pdf_content = ContentFile(advisor_pdf)
             advisor_obj = ExtractedAdvisor.objects.create(**advisor)
             advisor_obj.pdf_file.save('advisor_pdf.pdf', pdf_content)
             
        extracted_advisors_objects.append(advisor_obj)
        # print(' extracted_advisors_objects',extracted_advisors_objects)    
        serializer=ExtractAdvisorSerializer(extracted_advisors_objects,many=True) 
        return Response(serializer.data,status=status.HTTP_200_OK) 


        # extracted_advisors_content = ContentFile(extracted_advisors_list)
        
    def extract_advisor_data(self,pdf_file):
        
        pdf = PdfReader(pdf_file)  
        extracted_advisors_list =[]
        for page in pdf.pages:
             advisor_data={}
             advisor_data['name'] = self.extract_advisor_name(page)
             advisor_data['address']= self.extract_advisor_address(page)
             advisor_data['account_owner']= self.extract_account_owner(page)
             advisor_data['occupation']= self.extract_client_occupation(page)
             advisor_data['home_phone']= self.extract_client_phone(page)
             extracted_advisors_list.append(advisor_data)
        return extracted_advisors_list     
     
     
    def extract_advisor_name(self,pdf_page):
        
        advisor_name_pattern = r"Advisor\(s\):\s+(.+)"
        advisor_match = re.search(advisor_name_pattern, pdf_page.extract_text())
        if advisor_match:
            advisor_name = advisor_match.group(1).strip()
            if advisor_name:
                print('advisor_name',advisor_name)
                return advisor_name
        return ''
    
    def extract_advisor_address(self,pdf_page):
        address_pattern = r"([A-Z].+)(?:\r\n|\r|\n)"
        address_match = re.search(address_pattern,pdf_page.extract_text())
        if address_match:
            advisor_address = address_match.group(1).strip()
            if advisor_address:
              print('advisor_address',advisor_address)      
              return advisor_address
        return ''
    
    def extract_account_owner(self,pdf_page):
        
        account_owner_pattern =  r"Account Owner:\s*(.*)"
        owner_match = re.search( account_owner_pattern, pdf_page.extract_text())
        print(owner_match)
        if  owner_match:
            account_owner_name =  owner_match.group(1).strip()
            if account_owner_name:  # Exclude empty or None values
              print('account_owner_name:', account_owner_name)
              return account_owner_name
        return ''
    
    def extract_client_occupation(self,pdf_page):
        
        client_occupation_pattern = r"Occupation:\s*(.*)"
        occupation_match = re.search(client_occupation_pattern, pdf_page.extract_text())
        if occupation_match:
            client_occupation = occupation_match.group(1).strip()
            if client_occupation:
                print('client_occupation', client_occupation)
                return  client_occupation
        return ''    
       
    def extract_client_phone(self,pdf_page):
        
        client_phone_pattern = r"Home Phone:\s*(.*)"
        phone_match = re.search(client_phone_pattern, pdf_page.extract_text())
        if phone_match:
            client_phone = phone_match.group(1).strip()
            if client_phone:
                print('client_phone', client_phone)
                return client_phone
        return ''    
    
    
    def generate_advisor_pdf(self, advisor_data):
        # Use ReportLab to generate a PDF for the advisor based on the extracted data
        # Modify this code to create the PDF based on your requirements
        buffer = BytesIO()
        # Create a new PDF document
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Define table data and style
        table_data = [
        ['Name:', advisor_data['name']],
        ['Address:', advisor_data['address']],
        ['Account Owner:', advisor_data['account_owner']],
        ['Occupation:', advisor_data['occupation']],
        ['Home Phone:', advisor_data['home_phone']],
    ]
        table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Create the table and apply the style
        table = Table(table_data)
        table.setStyle(table_style)

    # Build the PDF document
        elements = [table]
        pdf.build(elements)

    # Get the PDF data from the buffer
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data
             
        # p = canvas.Canvas(buffer)

        # # Add advisor data to the PDF
        # p.drawString(100, 750, advisor_data['name'])
        # p.drawString(100, 730, advisor_data['address'] or '')
        # p.drawString(100, 710, advisor_data['account_owner'])
        # p.drawString(100, 690, advisor_data['occupation'])
        # p.drawString(100, 670, advisor_data['home_phone'])

        # # Save the PDF
        # p.save()
        # pdf_data = buffer.getvalue()
        # buffer.close()

        # return pdf_data 
     
class AllExtractedAdvisorViewSet(ModelViewSet):
    queryset =ExtractedAdvisor.objects.all()
    serializer_class = ExtractAdvisorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # def extract_advisor_data(self, pdf_file):
    #     # print('inside extract advisor data method')
     
    #     pdf = PdfReader(pdf_file)  
    #     # advisor_pattern = r"(?<=Advisor\(s\):\n)(.*?)(?=\n[A-Z])"
    #     # advisor_match = re.search(advisor_pattern, pdf.pages[0].extract_text(), re.DOTALL)
        
    #     advisor_pattern = r"Advisor\(s\):\s+(.+)"
    #     advisor_match = re.search(advisor_pattern, pdf.pages[0].extract_text())
    #     if advisor_match:
    #         advisor_name = advisor_match.group(1).strip()
    #         print('advisor_name',advisor_name)
        
    #     # address_pattern = r"([A-Z].+)(?:\r\n|\r|\n)([A-Z].+)(?:\r\n|\r|\n)([A-Z].+)(?:\r\n|\r|\n)([A-Z].+)(?:\r\n|\r|\n)([A-Z].+)(?:\r\n|\r|\n)(.+)"
    #     # address_match = re.search(address_pattern, pdf.pages[0].extract_text(), re.MULTILINE) 
    #     # if address_match:
    #     #     address_lines = [line.strip() for line in address_match.groups()]
    #     #     advisor_address=' '.join(address_lines)
    #     #     print('advisor_address',advisor_address.strip())  
    #     # print('pdf pages',pdf.pages[0].extract_text()) 
    #     address_pattern = r"CommonWealth[\s\S]+?(\n.+)"
    #     address_match = re.search(address_pattern, pdf.pages[0].extract_text())
    #     if address_match:
    #         advisor_address = address_match.group(1).strip()
    #         print('advisor_address',advisor_address)
        
        
        
        
         
    #     extracted_advisors=[]
    #     first_page=pdf.pages[0]
    #     # print('first_page',first_page)
    #     advisor_1={'name':first_page.extract_text(),'address':first_page.extract_text()}
    #     # print('first_advisor',advisor_1)
    #     extracted_advisors.append(advisor_1)
    #     # print('advisor list in extracted advisor data method',extracted_advisors)
    #     return extracted_advisors
    
    
    
    # def insert_data_into_database(self, data):
    #     ExtractedAdvisor.objects.create(**data)  
        
    
                 