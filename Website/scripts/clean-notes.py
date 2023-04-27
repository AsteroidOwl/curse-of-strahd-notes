from bs4 import BeautifulSoup
import sys

cleanContent = ''
with open(sys.argv[1], 'r+', encoding='utf-16') as my_file:
  text = my_file.read()
  soup = BeautifulSoup(text)
  
  # Make all non-absolute links relative to the root
  for a in soup.findAll('a'):
    if(not a['href'].startswith('http')):
      a['href'] = '/' + a['href']

  # Hide all the links in the session notes
  sessionNotes = soup.find(id="Session_1").find_parent(class_='block-language-dataviewjs')
  for a in sessionNotes.findAll('a'):
    a['href'] = '#'

  cleanContent = str(soup)

  my_file.seek(0)
  my_file.write(cleanContent)
  my_file.truncate()
  