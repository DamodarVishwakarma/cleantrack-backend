# import urllib.request
# import urllib.parse
#
#
# def sendSMS(apikey, numbers, sender, message):
#     data = urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
#                                    'message': message, 'sender': sender})
#     data = data.encode('utf-8')
#     request = urllib.request.Request("https://api.textlocal.in/send/?")
#     f = urllib.request.urlopen(request, data)
#     fr = f.read()
#     return (fr)
#
#
# resp = sendSMS('eFLzoYIflnA-wYlhcARhyQ2Eu1zq0sOoQ6vdZJYfbq', '8210279880',
#                'xyz', '7891019125')
# print(resp)