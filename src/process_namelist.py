def clean_list(names):
    clean_name_list = []
    for name in names:
        if ',' in name:
            ln, fn = splitfirstcomma(name)
            ln = ln.strip()
            fn = fn.strip()
            words = fn.split(' ')
            fn = splitnonalpha(words[0]).strip()
            clean_name_list.append((fn, ln))
        else:
            words = name.split(' ')
            if len(words) == 1:
                clean_name_list.append(('', words[0].strip()))
            else:
                ln = words[len(words) - 1].strip()
                fn = splitnonalpha(words[0]).strip()
                clean_name_list.append((fn, ln))

    return clean_name_list

def splitnonalpha(s):
    pos = 1
    while pos < len(s) and s[pos].isalpha():
        pos+=1
    return s[:pos]

def splitfirstcomma(s):
    pos = 1
    while pos < len(s) and s[pos] != ',':
        pos+=1
    return (s[:pos], s[pos+1:])

def process_file(filename):
    names = []    
    with open(filename, 'r') as file:
        for line in file:
            names.append(line.replace('\n', ''))
    return clean_list(names)