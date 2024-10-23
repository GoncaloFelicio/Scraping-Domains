import re
import csv
import scrapy


class MultiDomainSpider(scrapy.Spider):
    name = "multi_domain_spider"
    
    # Call the parent class init method with input arguments
    def __init__(self, domains_file=None, *args, **kwargs):
        super(MultiDomainSpider, self).__init__(*args, **kwargs)
        # Read domains one at a time using a generator
        self.domains_file = domains_file

    def start_requests(self):
        if self.domains_file:
            with open(self.domains_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    domain = row.get('domain')
                    if domain:
                        url = 'https://' + domain.strip()
                        yield scrapy.Request(url=url, callback=self.parse, errback=self.handle_error, meta={'domain': domain})

    def parse(self, response):
        # The extraction occurs here, methods to extract can be modified and added in this section
        domain = response.meta['domain']
        try: 
            # If status is not 200-OK, return error message and empty fields
            if response.status != 200:
                self.logger.error(f'Failed to retrieve {domain}, Status: {response.status}')
                yield {
                    'url': domain,
                    'status': response.status,
                    'title': [''],
                    'email': [''],
                    'phone': [''],
                    'address': [''],
                    'copyright': ['']
                }
                return
            
            page_title = self.extract_pageTitle(response)
            # Extract email information from href 'mailto:'
            email_text = self.extract_email(response)
            # Extract phone information from href 'tel:'
            phone_text = self.extract_phone(response)
            # Extract address information from href 'google/maps:'
            address_text = self.extract_address(response)
            # Extract copyright information
            copyright_text = self.extract_copyright(response)
            # copyright_text = ['']
            
            yield {
                'url': response.url,
                'status': response.status,
                'title': page_title,
                'email': email_text,
                'phone': phone_text,
                'address': address_text,
                'copyright': copyright_text
            }

        except Exception as e:
            # Log the error and yield an empty result for this domain
            self.logger.error(f"Error parsing domain: {domain}, error: {str(e).splitlines()[0]}")
            yield {
                'url': domain,
                'status': [f'Error: {str(e).splitlines()[0]}'],
                'title': [''],
                'email': [''],
                'phone': [''],
                'address': [''],
                'copyright': ['']
            }

    def handle_error(self, failure):
        # This method will be called if there is an error during the request
        domain = failure.request.meta['domain']
        self.logger.error(f"Request failed for domain: {domain}, error: {str(failure).splitlines()[0]}")
        yield {
            'url': domain,
            'status': [f'Error: {str(failure).splitlines()[0]}'],
            'title': [''],
            'email': [''],
            'phone': [''],
            'address': [''],
            'copyright': ['']
        }
    
    def extract_pageTitle (self, response):
        page_title = [response.xpath("normalize-space(//title/text())").get()]
        return page_title if page_title else ['']

    def extract_email(self, response):
        # Extract email information from href 'mailto:'
        emails =  response.xpath("normalize-space(//a[contains(@href, 'mailto:')]/@href)").getall()
        return emails if emails else ['']
    
    def extract_phone(self, response):
        # Extract email information from href 'mailto:'
        phones =  response.xpath("normalize-space(//a[contains(@href, 'tel:')]/@href)").getall()
        return phones if phones else ['']
        # Or use a regex expression to get phone number, tricky to account for all variations
        # phones = re.findall(r'\+31?0\d{9}', response.text) # works on issos.nl
                
    def extract_address(self, response):
        # Extract address information from href 'google/maps:'
        address =  response.xpath("normalize-space(//a[contains(@href, 'https://www.google.com/maps')]//text())").getall()
        return address if address else ['']

    def extract_copyright(self, response):
        # Extract copyright information from text containing 'Copyright'
        copyright_text =  response.xpath("normalize-space(//*[contains(text(), '©')]//text())").getall()
        return copyright_text if copyright_text else ['']
    