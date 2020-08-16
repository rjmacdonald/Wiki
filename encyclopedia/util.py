import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def markdown(content):
    """
    Converts markdown text to html, elements:
    Headings, lists(ul), paragraphs, bold and links
    """
    
    # Splits content into lines, initiates markdown list
    lines = re.split('\n', content)
    markdown = []
    
    for line in lines:

        # Scans each line for # and *
        # Counts each and stores position of first instance
        hash_position = re.search('[#]*', line)
        hash_count = len(hash_position.group())
        star_count = len(re.findall('\*', line))
        star_position = re.search('\*', line)

        # If # present at start, converts line to appropriate heading
        if hash_count > 0 and hash_position.start() == 0: 
            start = "<h" + str(hash_count) + ">"
            end = "</h" + str(hash_count) + ">"
            middle = re.sub('#|\\r', '', line)
            line = start + middle + end
        
        # If * present at start, converts line to list item
        elif star_count > 0 and star_position.start() == 0:
            middle = re.sub('\*', '', line, 1)
            line = "<li>" + re.sub('\\r', '', middle) + "</li>"
        
        # If not an empty line, converts to paragraph
        elif re.search('\w', line) != None:
            line = '<p>' + re.sub('\\r', '', line) + '</p>'
        
        # Assigns line breaks to empty lines
        else:
            line = '<br>'
        
        # Declares the emphasis marker and counts all instances
        emphasis = '\*\*'
        emphasis_count = len(re.findall(emphasis, line))

        # Loops through line while at least 2 instances present
        # First instance replaced by opening tag, second by closing
        while emphasis_count > 1:
            line = re.sub(emphasis, '<strong>', line, 1)
            line = re.sub(emphasis, '</strong>', line, 1)
            emphasis_count = len(re.findall(emphasis, line))
        
        # Declares link and href formats
        # Locates all instances in line
        link = '\[[^(]+\]'
        href = '\([^ ]+\)'
        links = re.findall(link, line)
        hrefs = re.findall(href, line)

        # Loops through each link, cleaning brackets
        for link in links:
            link = re.sub('\[', '\\[', link)
            link = re.sub('\]', '\\]', link)

            # Loops through each href, cleaning brackets
            # Count and if ensures only the enclosing brackets are affected
            for href in hrefs:
                count = len(re.findall('\)', href))
                if count > 1:
                    href = href.replace(')', '', 1)
                href = re.sub('\(', '\\(', href)
                href = re.sub('\)', '\\)', href, 1)
                
                # Searches line for currently selected href/link pair
                link_search = re.search(link, line)
                href_search = re.search(href, line)
                
                # If both present and concurrent replaces with link tag
                if link_search != None and href_search != None:
                    if link_search.end() == href_search.start():
                        print("pre-cleaning:", link_search.group(), href_search.group())
                        link_clean = re.sub('\[|\]', '', link_search.group())
                        href_clean = re.sub('\(|\)', '', href_search.group())
                        print("post-cleaning:", link_clean, href_clean)
                        replace = link + href
                        insert = '<a href="' + href_clean + '">' + link_clean + "</a>"
                        print("Replace = ", replace, "insert = ", insert)
                        line = re.sub(replace, insert, line)

        # Commits cleansed line to markdown list
        markdown.append(line)

    # Initialises variables
    item_count = 0
    list_active = 0

    # Loops each item of the markdown list, checking for list item tags
    for item in markdown:
        list_tag = re.search('<li>', item)

        # If tag found and list is not active
        # Inserts an unordered list opener, sets list to active 
        if list_tag != None and list_active == 0:
            markdown.insert(item_count, '<ul>')
            list_active = 1
        
        # Else if a non-list tage is found and list is active
        # Inserts a closing tag and sets list to inactive
        elif list_tag == None and list_active == 1:
            if re.search('<[a-z]+>', item) != None:
                markdown.insert(item_count, '</ul> ')
                list_active = 0
        
        # Iterates loop
        item_count += 1
    
    # Checks for an active list and appends a close tag if required
    # Safety for lists with list item as last in the list
    if list_active == 1:
        markdown.append('</ul> ')
        list_active = 0
    
    # Concatenates each list item from markdown into the html string
    html = ''
    for item in markdown:
        html += item
    return html