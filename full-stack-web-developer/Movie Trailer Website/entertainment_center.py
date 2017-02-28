import fresh_tomatoes
import media


# create a list of movie objects
city_of_angels = media.Movie("City of Angels",
                             "Inspired by the modern classic, Wings of Desire,"
                             "City involves an angel (Cage) who is spotted by a"
                             " doctor in an operating room.",
                             "http://br.web.img3.acsta.net/pictures/13/12/09/20/47/582823.jpg",
                             "https://www.youtube.com/watch?v=mwWL8cB2Ix8")

pulp_fiction = media.Movie("Pulp Fiction",
                           "Pulp Fiction is a 1994 American neo-noir crime black "
                           "comedy film written and directed by Quentin Tarantino",
                           "https://upload.wikimedia.org/wikipedia/en/3/3b/Pulp_Fiction_%281994%29_poster.jpg",
                           "https://www.youtube.com/watch?v=s7EdQ4FqbhY")

shining = media.Movie("The Shining",
                      "The Shining is a 1980 British-American psychological horror "
                      "film produced and directed by Stanley Kubrick.",
                      "https://upload.wikimedia.org/wikipedia/en/2/25/The_Shining_poster.jpg",
                      "https://www.youtube.com/watch?v=5Cb3ik6zP2I")

into_the_wild  = media.Movie("Into the Wild",
                    "After graduating from Emory University, top student and "
                    "athlete Christopher McCandless abandons his possessions and hitchhikes to Alaska.",
                    "http://www.be-a-woman.com/wp-content/uploads/2016/02/into-the-wild-movei.jpg",
                    "https://www.youtube.com/watch?v=g7ArZ7VD-QQ")


godfather = media.Movie("The Godfather",
                    "The aging patriarch of an organized crime dynastytransfers "
                    "control of his clandestine empire to his reluctant son.",
                    "http://wallpaperrs.com/uploads/movies/the-godfather-glamorous-hd-wallpaper-142942655111.jpg",
                    "https://www.youtube.com/watch?v=sY1S34973zA")


edward_scissorhands = media.Movie("Edward Scissorhands",
                    "A gentle man, with scissors for hands, is brought into "
                    "a new community after living in isolation.",
                    "https://images-na.ssl-images-amazon.com/images/I/71Mo1mkJWiL._SL1211_.jpg",
                    "https://www.youtube.com/watch?v=M94yyfWy-KI")


# stored objects in a list 
movies = [city_of_angels,pulp_fiction,shining,into_the_wild,godfather,edward_scissorhands]

# call the fresh_tomatoes to build the HTML file
fresh_tomatoes.open_movies_page(movies)

