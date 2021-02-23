import requests
import requests.auth
import json
import random

def createName():
    name = ""
    for i in range(4):
        name += chr(random.randint(65, 90))
    return name

def __main__():
    period = "week"
    # Authorise
    print("Authorising...")
    client_auth = requests.auth.HTTPBasicAuth('FDpgkXUyf-Jijw', 'zO9sILCFSQL7mJJATCvAHtXpzTc')
    post_data = {"grant_type" : "client_credentials"}
    user_agent = "windows:post-curator-for-reddit-test-script:v1.1 (by /u/snarlinger)" 
    headers = {"User-Agent" : user_agent}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
    if (response.status_code == 200):
        print("Authorised!")
        # Isolate bearer token
        response_json = response.json()
        token = response_json["access_token"]
        # Initialise headers
        headers = {"Authorization" : "bearer " + token, "User-Agent" : user_agent}
        # User input loop
        posts_retrieved = 0
        characters_range = (33, 126) # inclusive either side
        illegal_characters = [35, 37, 47, 63, 92]
        posts_range = (1, 100)
        subreddit_invalid = True
        while subreddit_invalid:
            subreddit = input("Which subreddit? Or type QUIT. ")
            if (len(subreddit) == 0):
                print("You didn't enter anything, dummy. Try again.")
                continue
            if (subreddit.casefold() == "quit"):
                return
            # Getting rid of trailing r/ or /r/
            if (subreddit[:2] == "r/"):
                subreddit = subreddit[2:]
            elif (subreddit[:3] == "/r/"):
                subreddit = subreddit[3:]
            if (subreddit == "+"):
                print("That isn't a subreddit. Try again.")
                continue
            # Ensuring valid characters
            characters_valid = True
            for ch in subreddit:
                if (ord(ch) < characters_range[0] or ord(ch) > characters_range[1]):
                    print("That isn't a subreddit. Try again.")
                    characters_valid = False
                    break
                for ill in illegal_characters:
                    if (ill == ord(ch)):
                        print("That isn't a subreddit. Try again.")
                        characters_valid = False
                        break
                else:
                    continue
                break
            if (characters_valid):
                subreddit_invalid = False;
        print("Valid subreddit name!")
        # Ensuring valid number of posts
        posts_invalid = True
        while posts_invalid:
            posts = input("How many posts? Minimum is " + str(posts_range[0]) + ", maximum is " + str(posts_range[1]) + ". Or type QUIT. ")
            if (posts.casefold() == "quit"):
                return
            if (not posts.isdigit()):
                print("That's not even a number! Try again.")
            elif (int(posts) < posts_range[0] or int(posts) > posts_range[1]):
                print("That's not in the specified range. Try again.")
            else:
                posts_invalid = False
        print("Valid number of posts!")
        params = {"t" : period, "limit" : posts}
        while True:
            # Retrieve images
            print("Requesting images...")
            response = requests.get("https://oauth.reddit.com/r/" + subreddit + "/top", params=params, headers=headers)
            if (response.status_code == 200):
                print("Request successful!")
                # The request was successful, so now we try to retrieve image data.
                response_json = response.json()
                try:
                    if (response_json["kind"] == "Listing"):
                        print("Navigating children...")
                        children = response_json["data"]["children"]
                        for post in children:
                            print("Next child...")
                            if (post["kind"] == "t3"):
                                print("Child is a link -- let's go")
                                post_url = post["data"]["url"]
                                # Check the filename extension's validity
                                print("Checking url's extension validity...")
                                extension = ""
                                if (post_url[-4:] == ".jpg" or post_url[-4:] == ".png"):
                                    extension = post_url[-4:]
                                elif (post_url[-5:] == ".jpeg"):
                                     extension = post_url[-5:]
                                if (extension != ""):
                                    print("The extension is valid!")
                                    # Start image stream
                                    print("GETting image stream...")
                                    response = requests.get(post_url, stream=True)
                                    if (response.status_code == 200):
                                        print("Response returned succesfully")
                                        while True:
                                            print("Creating image name...")
                                            name = createName()
                                            print("Created image name: " + name)
                                            print("Seeing if file with that name already exists...")
                                            try:
                                                # Try to read. If this works, we need a new file name (continue)
                                                open("images/" + name + extension)
                                                print("A file with that name already exists -- time to make a new one")
                                            except FileNotFoundError:
                                                # File doesn't exist -- let's create it and write the image to it
                                                print("File doesn't exist. Writing to images folder...")
                                                chunks = []
                                                #with open("images/" + name + extension, "wb") as f:
                                                for chunk in response:
                                                    chunks.append(chunk)
                                                    #chunks += str(chunk)
                                                    #f.write(chunk)
                                                with open("images/" + name + extension, "wb") as f:
                                                    for chunk in chunks:
                                                        f.write(chunk)
                                                #print("Chunks list: " + str(chunks))
                                                print("Image written to: " + name + extension)
                                                #print("Chunks: " + chunks)
                                                break
                                    else:
                                        print("Request failed with a status code of " + str(response.status_code))
                                        print("JSON representation:")
                                        try:
                                            print(response.json())
                                        except json.decoder.JSONDecodeError:
                                            print("JSONDecodeError.")
                                        print("Moving onto the next image")
                                else:
                                    print("The extension isn't valid. This is the URL: " + post_url)
                                    print("Moving onto the next image")
                            else:
                                print("Child isn't a link. This is the kind: " + post["kind"])
                                print("Moving onto the next child")
                        print("All children have been retrieved! Restarting...")
                        posts_retrieved += len(children)
                        # User input w/ count and after values
                        posts_invalid = True
                        while posts_invalid:
                            posts = input("How many posts? Minimum is " + str(posts_range[0]) + ", maximum is " + str(posts_range[1]) + ". Or type QUIT. ")
                            if (posts.casefold() == "quit"):
                                return
                            if (not posts.isdigit()):
                                print("That's not even a number! Try again.")
                            elif (int(posts) < posts_range[0] or int(posts) > posts_range[1]):
                                print("That's not in the specified range. Try again.")
                            else:
                                posts_invalid = False
                        print("Valid number of posts!")
                        params = {"t" : period, "limit" : posts, "count" : posts_retrieved, "after" : response_json["data"]["after"]}
                    else:
                        print("Message is malformed: the kind is not a Listing, but a " + response_json["kind"])
                        try:
                            print(response.json())
                        except json.decoder.JSONDecodeError:
                            print("JSONDecodeError.")
                        print(response_json)
                except KeyError:
                    print("KeyError...")
                    
            else:
                print("Request failed with a status code of " + str(response.status_code))
                print("JSON representation:")
                try:
                    print(response.json())
                except json.decoder.JSONDecodeError:
                    print("JSONDecodeError.")
    else:
        print("Authorisation unsuccessful, status code of " + str(response.status_code))
        print("JSON representation:")
        try:
            print(response.json())
        except json.decoder.JSONDecodeError:
            print("JSONDecodeError.")

__main__()
print("Quitting...")
