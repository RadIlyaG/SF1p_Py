import ftplib


def login():
    try:
        ftp = ftplib.FTP('ftp.rad.co.il', 'ate', 'ate2009')
        ftp.encoding = "utf-8"
        ftp.cwd('sf1v')
        return ftp
    except Exception as err:
        print(f'Lib_ftp login Error: {err}')
        return None


def upload_file(fil):
    ftp = login()
    ret = -1
    if ftp is not None:
        with open(fil, "rb") as file:
            ftp.storbinary(f"STOR {fil}", file)

        # Get list of files
        print(f'upload_file {fil} {ftp.nlst()}')
        ftp.quit()
        ret = 0
    return ret


def get_file(rem_fil, loc_fil):
    ftp = login()
    ret = -1
    rem_fil = rem_fil.lower()
    if ftp is not None:
        if rem_fil in ftp.nlst():
            with open(loc_fil, "wb") as file:
                # Command for Downloading the file "RETR filename"
                ftp.retrbinary(f"RETR {rem_fil}", file.write)

        ftp.quit()
        ret = 0
    return ret


def delete_file(fil):
    ftp = login()
    fil = fil.lower()
    ret = -1
    if ftp is not None:
        if fil in ftp.nlst():
            ftp.delete(fil)

        ftp.quit()
        ret = 0
    return ret


def file_exist(fil):
    ftp = login()
    ret = -1
    fil = fil.lower()
    if ftp is not None:
        if fil in ftp.nlst():
            ret = True
        else:
            ret = False

        ftp.quit()
    return ret
