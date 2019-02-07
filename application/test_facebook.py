import facebook

token = "EAADQal1aLdABACKrgmeew9VMvEvJBffX9Ewqqro9cwuv0Y0DEwsSVw1XNF6vjk8tsD0fH9pE601XUhmKZA6rdPbC3yN2SmEUWuO5AwZArrBQVFyjKIIFJcZCUZCcZB8S58MclvTmIoI2v9VQtAijjWxlrChJs2eh2213UPP42k1OnnBJ3KOj8rKMZAcarInQjhv2mwPotwVwZDZD"

graph = facebook.GraphAPI(token)

args = {'fields' : 'birthday,name' }
friends = graph.get_object("me/friends",**args)

print((friends))