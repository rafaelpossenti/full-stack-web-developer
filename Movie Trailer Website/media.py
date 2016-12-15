class Movie():

    """This is a class responsible to create new movies 
    
    Attributes:
        title (str)...............: Title of the film.
        storyLine (str)...........: storyline of the film.
        poster_image_url (str)....: stored a link to an image of the film.
        trailer_youtube_url (str).: stored a link to a trailer of youtube.
   
    """
    
    def __init__(self,movie_title,movie_storyline,poster_image,
                 trailer_youtube):
        self.title               = movie_title
        self.storyline           = movie_storyline
        self.poster_image_url    = poster_image
        self.trailer_youtube_url = trailer_youtube 
    
    
