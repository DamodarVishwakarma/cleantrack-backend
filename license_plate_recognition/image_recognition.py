# import mimetypes
# import os
# from wsgiref.util import FileWrapper
# from django.http import HttpResponse


def license_plate_recognition(image_url):
    # import cv2
    # import imutils
    # import pytesseract
    #
    # # pytesseract.pytesseract.tesseract_cmd = '/home/pc-d/digitalplatformbackend/venv/bin/pytesseract'
    #
    # image = cv2.imread(image_url)
    #
    # image = imutils.resize(image, width=500)
    # # cv2.imshow("original image", image)
    # # cv2.waitKey(0)
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # # cv2.imshow('gray scle image ', gray)
    # # cv2.waitKey(0)
    # gray = cv2.bilateralFilter(gray, 11, 17, 17)
    # # cv2.imshow("2- gray scale image ", gray)
    # # cv2.waitKey(0)
    #
    # edged = cv2.Canny(gray, 170, 200)
    # # cv2.imshow("Canny Edge ", edged)
    # # cv2.waitKey(0)
    #
    # cnts, new = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #
    # img1 = image.copy()
    # cv2.drawContours(img1, cnts, -1, (0, 255, 0), 3)
    # # cv2.imshow("all counter ", img1)
    # # cv2.waitKey(0)
    #
    # cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:30]
    # NumberPlateCnt = None
    #
    # img2 = image.copy()
    # cv2.drawContours(img2, cnts, -1, (0, 255, 0), 3)
    # # cv2.imshow("Top 30 Contours",img2)
    # # cv2.waitKey(0)
    #
    # count = 0
    # idx = 1
    # for c in cnts:
    #     peri = cv2.arcLength(c, True)
    #     approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    #     if len(approx) == 4:
    #         NumberPlateCnt = approx
    #         x, y, w, h = cv2.boundingRect(c)
    #         new_img = image[y:y + h, x:x + w]
    #         cv2.imwrite("ocr_image/Images/" + str(idx) + ".png", new_img)
    #
    #         idx += 1
    #
    #         break
    # try:
    #     cv2.drawContours(image, [NumberPlateCnt], -1, (0, 255, 0), 3)
    # except:
    #     pass
    # # cv2.imshow("final image ", image)
    # # cv2.waitKey(0)
    #
    # crop_img_loc = 'ocr_image/Images/1.png'
    #
    # # cv2.imshow("crped image ", cv2.imread(crop_img_loc))
    #
    # license_string = pytesseract.image_to_string(crop_img_loc, lang='eng')
    #
    # # print("Number is : ", text)
    # # cv2.waitKey(0)
    #
    # # license_string = ''
    #
    # text = [character for character in license_string if character.isalnum() ]
    # text = "".join(text)
    text=""
    return text

# def get_file_logs(image):
#     wrapper = FileWrapper(open(image.file, 'rb'))
#     content_type = mimetypes.guess_type(image)[0]
#     response = HttpResponse(wrapper, content_type=content_type)
#     response['Content-Disposition'] = 'attachment; filename={0}'.format(os.path.basename(image))
#     os.remove(image)
#     return response

# def download_image(image):
#     wrapper = FileWrapper(open(image.file))  # img.file returns full path to the image
#     content_type = mimetypes.guess_type(image)[0]  # Use mimetypes to get file type
#     response = HttpResponse(wrapper, content_type=content_type)
#     response['Content-Length'] = os.path.getsize(image.file)
#     response['Content-Disposition'] = "attachment; filename=%s" % image.name
#     return response
