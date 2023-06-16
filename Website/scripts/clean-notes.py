import os
import sys
import shutil
from bs4 import BeautifulSoup

alreadyFixedLinkClass = 'keep-link'

def overwriteFile(file, soup):
  content = str(soup)
  file.seek(0)
  file.write(content)
  file.truncate()

def removeUrls(soup):
  for a in soup.find_all('a', class_='internal-link'):
    a.wrap(soup.new_tag('b'))
    a.unwrap()

def fixUrls(soup):
  for a in soup.find_all('a', class_='internal-link'):
    a['rel'] = ''
    a['data-href'] = ''

def removeSidebar(soup):
  treeContainer = soup.find(class_='tree-container')
  treeContainer.decompose()

def updateRootPath(soup, rootPath):
  meta = soup.find(id='root-path')
  meta['root-path'] = '/' + rootPath

def fixImages(soup):
  images = soup.select('.image-embed>img')
  for image in images:
    image['src'] = '/' + image['src']

def removeLinksInFile(fname):
  with open(fname, 'r+') as handle:
    soup = BeautifulSoup(handle.read(), 'html.parser')
    print('Removing URLs for: {}'.format(fname))
    removeUrls(soup)

    overwriteFile(handle, soup)

def fixUrlsInFile(fname):
  with open(fname, 'r+') as handle:
    soup = BeautifulSoup(handle.read(), 'html.parser')
    print('Fixing URLs for: {}'.format(fname))
    fixUrls(soup)

    overwriteFile(handle, soup)

def fixAssetsInFile(fname):
  with open(fname, 'r+') as handle:
    soup = BeautifulSoup(handle.read(), 'html.parser')
    print('Fixing Assets for: {}'.format(fname))
    fixImages(soup)

    overwriteFile(handle, soup)

def removeDynamicLinks(soup):
  classes = ['internal-link', 'footnote-link', 'tree-item-link']
  internalLinks = soup.find_all('a', class_= lambda c: c in classes)

def updateAllFiles(folder):
  for root, dirnames, filenames in os.walk(folder):
    for filename in filenames:
      if filename.endswith('.html'):
        fname = os.path.join(root, filename)
        with open(fname, 'r+') as handle:
          soup = BeautifulSoup(handle.read(), 'html.parser')
          print('Removing Sidebar for: {}'.format(fname))
          removeSidebar(soup)
          print('Updating Root Path for: {}'.format(fname))
          updateRootPath(soup, folder)
          print('Removing dynamic links for: {}'.format(fname))
          removeDynamicLinks(soup)

          overwriteFile(handle, soup)

def importAndCleanLinkedFiles(soup, spoilersFolder, rootSiteFolder):
  for a in soup.find_all('a', class_='internal-link'):
    if alreadyFixedLinkClass in a.get('class', []):
      print('link already fixed: {}'.format(newPath))
      continue

    relativePath = os.path.join(*a['href'].split('/'))
    newPath = os.path.join(spoilersFolder, relativePath)
    if os.path.isfile(newPath):
      print('file already exists: {}'.format(newPath))
      continue
    
    origPath = os.path.join(rootSiteFolder, relativePath)
    print('copying {} -> {}'.format(origPath, newPath))
    os.makedirs(os.path.dirname(newPath), exist_ok=True)
    shutil.copyfile(origPath, newPath)
    removeLinksInFile(newPath)
    fixAssetsInFile(newPath)


def importLinkedFilesForFolder(spoilersFolder, rootSiteFolder):
  for root, dirnames, filenames in os.walk(spoilersFolder):
    for filename in filenames:
      if filename.endswith('.html'):
        fname = os.path.join(root, filename)
        with open(fname, 'r+') as handle:
          soup = BeautifulSoup(handle.read(), 'html.parser')
          print('Parsing for linked files: {}'.format(fname))
          importAndCleanLinkedFiles(soup, spoilersFolder, rootSiteFolder)
          print('Fixing Urls: {}'.format(fname))
          fixUrls(soup)
          overwriteFile(handle, soup)




rootSpoilersFolder = sys.argv[1]
rootMainSiteFolder = sys.argv[2]
importLinkedFilesForFolder(rootSpoilersFolder, rootMainSiteFolder)
updateAllFiles(rootSpoilersFolder)
