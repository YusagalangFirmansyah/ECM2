import sys

with open('bsp-app/drafter_list_event_handler.txt', 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = "  lv_dms_numparts = request->num_multiparts( )."
end_marker = "    REPLACE ALL OCCURRENCES OF cl_abap_char_utilities=>cr_lf IN GV_MESSAGE WITH space."

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_marker)
    
    new_logic = "\"\"  DATA: lv_success_file_cnt TYPE i VALUE 0.
  
  lv_dms_numparts = request->num_multiparts( ).
  lv_dms_idx = 1.
  WHILE lv_dms_idx <= lv_dms_numparts.
    lo_dms_entity = request->get_multipart( lv_dms_idx ).
    IF lo_dms_entity->get_header_field( 'content-disposition' ) CS 'name="dms_file"'.
      lv_dms_filebin = lo_dms_entity->get_data( ).
      lv_dms_filename = lo_dms_entity->get_header_field( '~content_filename' ).
      
      IF lv_dms_filebin IS NOT INITIAL AND lv_dms_filename IS NOT INITIAL.
        " Format nama file agar sesuai standard ZUPLOAD_CS_AUTO (Contoh: DRW_30013196_filename.dwg)
        DATA: lv_final_filename TYPE string,
              lv_al11_path      TYPE string.
        
        CONCATENATE lv_dms_dokar '_' lv_dms_matnr '_' lv_dms_filename INTO lv_final_filename.
        CONCATENATE '/mnt/sap_media/engineering/' lv_final_filename INTO lv_al11_path.
      
        " Simpan ke AL11
        OPEN DATASET lv_al11_path FOR OUTPUT IN BINARY MODE.
        IF sy-subrc = 0.
          TRANSFER lv_dms_filebin TO lv_al11_path.
          CLOSE DATASET lv_al11_path.
          lv_success_file_cnt = lv_success_file_cnt + 1.
        ENDIF.
      ENDIF.
    ENDIF.
    lv_dms_idx = lv_dms_idx + 1.
  ENDWHILE.

  " Pengecekan
  IF lv_success_file_cnt = 0.
    GV_MESSAGE = 'File gagal ditangkap. Pastikan ukuran tidak melebihi batas server.'.
    GV_ICON    = 'error'.
    CONCATENATE 'drafter_list.htm?u=' GV_USER_ID '&r=' GV_ROLE '&n=' GV_FULL_NAME '&msg=' GV_MESSAGE '&icon=' GV_ICON INTO lv_url.
    navigation->goto_page( lv_url ). RETURN.
  ENDIF.

  " Jalankan ZECM_DMS_UPLOAD secara SYNCHRONOUS untuk memproses semua file yang sudah dikirim ke AL11
  SUBMIT zecm_dms_upload
    WITH p_dir = '/mnt/sap_media/engineering'
    WITH p_test = space
    EXPORTING LIST TO MEMORY
    AND RETURN.

  TYPES: BEGIN OF ty_log,
           file   TYPE string,
           doknr  TYPE draw-doknr,
           dokvr  TYPE draw-dokvr,
           dokar  TYPE draw-dokar,
           ctcode TYPE c LENGTH 6,
           status TYPE c LENGTH 10,
           msgty  TYPE c LENGTH 1,
           msgid  TYPE symsgid,
           msgno  TYPE symsgno,
           msgv1  TYPE symsgv,
           msgv2  TYPE symsgv,
           msgv3  TYPE symsgv,
           msgv4  TYPE symsgv,
           msg    TYPE string,
         END OF ty_log.
  DATA: lt_upload_log TYPE STANDARD TABLE OF ty_log,
        ls_upload_log TYPE ty_log.

  IMPORT log = lt_upload_log FROM MEMORY ID 'ZECM_DMS_LOG'.
  FREE MEMORY ID 'ZECM_DMS_LOG'.

  IF lt_upload_log IS INITIAL.
    GV_MESSAGE = 'File gagal diproses SAP (ZECM_DMS_UPLOAD gagal dieksekusi atau tidak mengirim respon memori).'.
    GV_ICON    = 'error'.
  ELSE.
    DATA: lv_err_cnt TYPE i VALUE 0,
          lv_suc_cnt TYPE i VALUE 0,
          lv_err_msg TYPE string.

    LOOP AT lt_upload_log INTO ls_upload_log.
      IF ls_upload_log-msgty = 'E' OR ls_upload_log-status = 'ERROR' OR ls_upload_log-status = 'SKIP'.
        lv_err_cnt = lv_err_cnt + 1.
        IF lv_err_msg IS INITIAL.
          lv_err_msg = ls_upload_log-msg.
        ENDIF.
      ELSE.
        lv_suc_cnt = lv_suc_cnt + 1.
      ENDIF.
    ENDLOOP.

    IF lv_err_cnt > 0.
      GV_MESSAGE = |Upload Selesai: { lv_suc_cnt } Sukses, { lv_err_cnt } Gagal ({ lv_err_msg })|.
      GV_ICON    = 'warning'.
    ELSE.
      GV_MESSAGE = |{ lv_suc_cnt } File berhasil di-upload dan terintegrasi ke BOM!|.
      GV_ICON    = 'success'.
    ENDIF.
  ENDIF.

  " Bersihkan karakter kutip agar tidak merusak Syntax JavaScript di UI
  REPLACE ALL OCCURRENCES OF '''' IN GV_MESSAGE WITH space.
  REPLACE ALL OCCURRENCES OF '|' IN GV_MESSAGE WITH space.
  REPLACE ALL OCCURRENCES OF '"' IN GV_MESSAGE WITH space.
  REPLACE ALL OCCURRENCES OF cl_abap_char_utilities=>newline IN GV_MESSAGE WITH space.
  REPLACE ALL OCCURRENCES OF cl_abap_char_utilities=>cr_lf IN GV_MESSAGE WITH space."\"\"
    
    new_content = content[:start_idx] + new_logic + content[end_idx:]
    with open('bsp-app/drafter_list_event_handler.txt', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Success by index!")
else:
    print("Could not find boundaries")
