
with open('log/query.txt', 'r', encoding='utf-8') as f:
    content = f.read().strip()
    print(content)
    # print(repr(content))
    if 'case' in content:
        print('case')