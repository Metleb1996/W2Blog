from core.constants.media_extentions import M_EXTENTIONS

def ext_cont(file_name):
   return '.' in file_name and \
   file_name.rsplit('.', 1)[1].lower() in M_EXTENTIONS
