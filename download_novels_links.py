import BiQuGeDownloader

entryUrl = 'http://www.biqugex.com/book_37/'
hunter = BiQuGeDownloader.BiQuGeDownloader(entryUrl)
str_of_result = hunter.open_url_return_str(entryUrl)
