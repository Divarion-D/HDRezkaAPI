from HDRezkaAPI import *

# search_text = input('Поиск: ')
search_text = 'Рик и Морти'
search_result = Search(search_text)

print(search_result)

# title_id = int(input('Введите номер: '))
title_id = 1
movie_data = search_result.get_data(title_id)
movie_info = MovieInfo(movie_data)
print(movie_info)
download_data = movie_info.get_data()


downloader = Download(download_data)

print(movie_info)

download_type = int(input('1 - Скачать фильм\n2 - Скачать сезон сериала\n3 - Скачать эпизоды сериала\n'
                          'Выберите тип скачивания: '))
if download_type == 1:
    downloader.download_movie()
    print('Скачивание успешно завершено!')
elif download_type == 2:
    season = int(input('Введите номер сезона: '))
    downloader.download_season(season)
    print('Скачивание успешно завершено!')
elif download_type == 3:
    correct_episode = False
    season = int(input('Введите номер сезона: '))
    episodes_count = download_data['seasons_episodes_count'][season]
    print(f'В данном сезоне количество эпизодов: {episodes_count}')
    start = int(input('Введите стартовый эпизод: '))
    end = int(input('Введите конечный эпизод: '))
    while not correct_episode:
        try:
            downloader.download_episodes(season, start, end)
            correct_episode = True
        except EpisodeNumberIsOutOfRange:
            print('Неверный диапазон!')
            episode = int(input('Снова введите диапазон эпизодов: '))
    print('Скачивание успешно завершено!')
else:
    print('Неверный тип скачивания!')
