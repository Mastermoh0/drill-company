import copy
from bs4 import BeautifulSoup

files = [
    'index.html', 'about.html', 'services.html', 'equipment.html', 
    'projects.html', 'why-choose-us.html', 'contact.html'
]

# Get the base HTML
with open('index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

head_div = soup.find('header').find('div', class_=lambda c: c and 'max-w-7xl' in c)
if head_div:
    head_div['class'] = [c.replace('px-8', 'px-4').replace('md:px-8', '') + ' md:px-8' if 'px-8' in c else c for c in head_div.get('class', [])]
    head_div['class'] = ' '.join(c for c in head_div['class'] if c).split() # normalize
    
    quote_btn = head_div.find('a', string=lambda t: t and 'GET QUOTE' in t.upper())
    if quote_btn:
        cls = quote_btn.get('class', [])
        if 'hidden' not in cls:
            quote_btn['class'] = cls + ['hidden', 'md:block']
    
    # Add Hamburger
    if not head_div.find('button', id='mobile-menu-btn'):
        btn = soup.new_tag('button', id='mobile-menu-btn')
        btn['class'] = "md:hidden text-on-background focus:outline-none ml-2"
        span = soup.new_tag('span', **{'data-icon': 'menu'})
        span['class'] = "material-symbols-outlined text-3xl"
        span.string = 'menu'
        btn.append(span)
        head_div.append(btn)

# Create Mobile Menu overlay
if not soup.find('div', id='mobile-menu'):
    menu_div = soup.new_tag('div', id='mobile-menu')
    menu_div['class'] = 'hidden fixed top-0 right-0 h-screen w-screen bg-[#f7fafc] z-50 flex-col items-center justify-center gap-8'
    
    close_btn = soup.new_tag('button', id='close-menu-btn')
    close_btn['class'] = "absolute top-6 right-6 text-on-background focus:outline-none"
    c_span = soup.new_tag('span', **{'data-icon': 'close'})
    c_span['class'] = "material-symbols-outlined text-4xl"
    c_span.string = 'close'
    close_btn.append(c_span)
    menu_div.append(close_btn)
    
    # clone nav links
    nav = soup.find('nav', class_=lambda c: c and 'hidden' in c)
    if nav:
        for a in nav.find_all('a'):
            ma = soup.new_tag('a', href=a['href'])
            ma['class'] = "mobile-nav-link text-2xl font-headline tracking-widest font-bold text-[#4c616c] hover:text-[#a23904]"
            ma.string = a.string
            menu_div.append(ma)
            
    # clone quote
    qa = soup.new_tag('a', href='contact.html')
    qa['class'] = "mt-4 bg-primary text-on-primary px-8 py-3 rounded font-label text-sm uppercase tracking-widest"
    qa.string = "GET QUOTE"
    menu_div.append(qa)

    soup.find('header').append(menu_div)

# Fix Footer sizing
foot = soup.find('footer')
if foot:
    foot_div = foot.find('div', class_=lambda c: c and 'max-w-7xl' in c)
    if foot_div:
        new_cls = []
        for c in foot_div.get('class', []):
            if c == 'px-8': new_cls.extend(['px-4', 'md:px-8'])
            elif c == 'py-12': new_cls.extend(['py-8', 'md:py-12'])
            else: new_cls.append(c)
        foot_div['class'] = new_cls

base_header = soup.find('header')
base_footer = soup.find('footer')

def set_active(header_soup, active_text):
    nav = header_soup.find('nav', class_=lambda c: c and 'hidden md:flex' in c)
    mobile_links = header_soup.find_all('a', class_=lambda c: c and 'mobile-nav-link' in c)
    if not nav: return
    
    curr_active = "text-[#a23904] border-b-2 border-[#a23904] pb-1 hover:text-[#a23904] transition-colors duration-200"
    inactive = "text-[#4c616c] dark:text-[#e0e3e5] font-medium hover:text-[#a23904] transition-colors duration-200"
    
    for a in nav.find_all('a'):
        a['class'] = inactive
        if a.string and a.string.strip().upper() == active_text.upper():
            a['class'] = curr_active
            
    for a in mobile_links:
        # Just tint mobile text to orange if active
        a['class'] = "mobile-nav-link text-2xl font-headline tracking-widest font-bold text-[#4c616c] hover:text-[#a23904]"
        if a.string and a.string.strip().upper() == active_text.upper():
            a['class'] = "mobile-nav-link text-2xl font-headline tracking-widest font-bold text-[#a23904]"

active_map = {
    'index.html': 'HOME',
    'about.html': 'ABOUT',
    'services.html': 'SERVICES',
    'equipment.html': 'EQUIPMENT',
    'projects.html': 'PROJECTS',
    'why-choose-us.html': 'WHY US',
    'contact.html': 'CONTACT'
}

for filename in files:
    with open(filename, 'r', encoding='utf-8') as f:
        file_soup = BeautifulSoup(f.read(), 'html.parser')
    
    old_h = file_soup.find('header')
    old_f = file_soup.find('footer')
    
    # We must deepcopy because bs4 attaches elements to the tree
    new_h = copy.copy(base_header)
    new_f = copy.copy(base_footer)
    
    set_active(new_h, active_map[filename])
    
    if old_h: old_h.replace_with(new_h)
    else: file_soup.body.insert(0, new_h)
    
    if old_f: old_f.replace_with(new_f)
    else: file_soup.body.append(new_f)
    
    with open(filename, 'w', encoding='utf-8') as out_f:
        out_f.write(str(file_soup))

print('Mobile HTML patched.')
