def list_pages(page, sum):
    '''Функция выдающая список строк для отображения страниц, как тем в форме, так и сообщений в теме'''
    if sum < 8:
        return [str(x) for x in range(1,sum+1)]
    if page < 5:
        return ['1','2','3','4','5','...',str(sum)]
    if page > sum-4:
        return ['1','...',str(sum-5),str(sum-4),str(sum-3),str(sum-2),str(sum-1),str(sum)]
    return ['1', '...', str(page-2), str(page-1), str(page), str(page+1), str(page+2), '...', str(sum)]


for page in range(1,21):
    print(page,'=', list_pages(page,20))