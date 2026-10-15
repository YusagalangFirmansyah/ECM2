import re

with open('bsp-app/dms_detail.htm', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = re.compile(r'<!-- \? Files Section -->.*?<!-- \? Status Log Timeline -->', re.DOTALL)

replacement = '''<!-- ? Files Section (List View) -->
    <%
      DATA: ls_file      TYPE cvapi_doc_file,
            lv_file_idx  TYPE i,
            lv_file_url  TYPE string,
            lv_file_name TYPE string,
            lt_fname     TYPE TABLE OF string,
            lv_fname_cnt TYPE i.
    %>
    <% IF mt_files IS NOT INITIAL. %>
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm mb-5 p-5">
      <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wide mb-4">
        <i class="fas fa-paperclip mr-2 text-slate-400"></i> File Original (Lampiran)
      </h3>
      <div class="flex flex-col gap-3">
    <% LOOP AT mt_files INTO ls_file. %>
    <%   lv_file_idx = sy-tabix. %>
    <%
         CLEAR: lt_fname, lv_file_name.
         SPLIT ls_file-filename AT '/' INTO TABLE lt_fname.
         DESCRIBE TABLE lt_fname LINES lv_fname_cnt.
         READ TABLE lt_fname INDEX lv_fname_cnt INTO lv_file_name.
         IF lv_file_name IS INITIAL.
           lv_file_name = ls_file-description.
         ENDIF.
         IF lv_file_name IS INITIAL.
           lv_file_name = |File { lv_file_idx }|.
         ENDIF.

         lv_file_url = |dms_detail_download.htm?DOKNR={ lv_doknr_disp }| &&
                       |&DOKAR={ ms_header-documenttype }| &&
                       |&DOKVR={ ms_header-documentversion }| &&
                       |&DOKTL={ ms_header-documentpart }| &&
                       |&ORIGTP={ lv_file_idx }|.
    %>
        <div class="flex items-center justify-between p-3 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-lg bg-brand-50 flex items-center justify-center text-brand-600 shrink-0">
              <i class="fas fa-file-alt text-xl"></i>
            </div>
            <div>
              <div class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wide mb-0.5">File <%= lv_file_idx %></div>
              <div class="text-sm font-semibold text-slate-700 break-all"><%= lv_file_name %></div>
            </div>
          </div>
          <a href="<%= lv_file_url %>" target="_blank" class="shrink-0 ml-4 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm inline-flex items-center gap-2">
            <i class="fas fa-download"></i> Download
          </a>
        </div>
    <% ENDLOOP. %>
      </div>
    </div>
    <% ENDIF. %>

    <!-- ? Status Log Timeline -->'''

new_content = pattern.sub(replacement, content)

with open('bsp-app/dms_detail.htm', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replaced with Python!")
