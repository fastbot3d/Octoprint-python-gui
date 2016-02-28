#!/usr/bin/env python

import wx
from wx import xrc
import  wx.lib.newevent

import sys
import  time
import  thread
import threading

#----------------------------------------------------------------------

# This creates a new Event class and a EVT binder function
(UpdateUIEvent, EVT_UPDATE_UI) = wx.lib.newevent.NewEvent()

from octoprint.octoprint import Connection_api, Job_api, File_api, Print_api

GUI_FILENAME = "bbp.xrc"
GUI_MAINFRAME_NAME = "frame_1"

class MyApp(wx.App):
    def OnInit(self):
        self.res = xrc.XmlResource(GUI_FILENAME)
        self._cur_sel_file = None
        self._cur_sel_file_orign = "local"
        
        self.InitFrame()
        self.BindFunction()
        self.InitLoadData()
        
        self.frame.Show()        
        return True
    
    def InitFrame(self):
        self.frame = self.res.LoadFrame(None, GUI_MAINFRAME_NAME)
        self.label_bed = xrc.XRCCTRL(self.frame, "label_bed")
        #self.label_bed.SetLabel("sdfsdf")
        self.label_ext1 = xrc.XRCCTRL(self.frame, "label_ext1")
        self.label_ext2 = xrc.XRCCTRL(self.frame, "label_ext2")
        self.label_ext3 = xrc.XRCCTRL(self.frame, "label_ext3")       
        self.combo_box_profile = xrc.XRCCTRL(self.frame, "combo_box_profile")
        self.button_connect = xrc.XRCCTRL(self.frame, "button_connect")
       

        #notebook_main
        self.notebook_main = xrc.XRCCTRL(self.frame, "notebook_main")
        self.notebook_main_print = xrc.XRCCTRL(self.notebook_main, "notebook_main_print")        
        #print 
        self.label_status = xrc.XRCCTRL(self.notebook_main_print, "label_status")
        self.label_file = xrc.XRCCTRL(self.notebook_main_print, "label_file")
        self.label_timelapse = xrc.XRCCTRL(self.notebook_main_print, "label_timelapse")
        self.label_total_time = xrc.XRCCTRL(self.notebook_main_print, "label_total_time")
        self.label_print_time = xrc.XRCCTRL(self.notebook_main_print, "label_print_time")
        self.label_print_left = xrc.XRCCTRL(self.notebook_main_print, "label_print_left")        
        self.button_print = xrc.XRCCTRL(self.notebook_main_print, "button_print")
        self.button_pause = xrc.XRCCTRL(self.notebook_main_print, "button_pause")
        #self.button_pause.SetLabel("sdfsdf")
        self.button_cancel = xrc.XRCCTRL(self.notebook_main_print, "button_cancel")
        
        #notebook_files
        self.notebook_files = xrc.XRCCTRL(self.notebook_main_print, "notebook_files")
        self.notebook_files_local = xrc.XRCCTRL(self.notebook_files, "notebook_files_local")
        self.notebook_files_sd = xrc.XRCCTRL(self.notebook_files, "notebook_files_sd")
        
        self.list_ctrl_local_file = xrc.XRCCTRL(self.notebook_files_local, "list_ctrl_local_file")
        self.list_ctrl_sd_file = xrc.XRCCTRL(self.notebook_files_sd, "list_ctrl_local_sd")
        
        self.button_refresh_file = xrc.XRCCTRL(self.notebook_main_print, "button_refresh_file")
        self.button_init_sd = xrc.XRCCTRL(self.notebook_main_print, "button_init_sd")
        self.button_eject_sd = xrc.XRCCTRL(self.notebook_main_print, "button_eject_sd")

        
        
        print("lkj 3")
        
        
    def BindFunction(self):
        self.button_connect.SetDefault() #default focus 
        self.Bind(wx.EVT_COMBOBOX, self.OnSelectProfile, self.combo_box_profile)  
        #self.Bind(wx.EVT_TEXT, self.OnSelectProfile, self.combo_box_profile)  
        #self.Bind(wx.EVT_TEXT_ENTER, self.OnSelectProfile, self.combo_box_profile)  
        
        self.Bind(wx.EVT_BUTTON, self.OnConnectOrDisconnect, self.button_connect)           
        self.Bind(wx.EVT_BUTTON, self.OnPrint, self.button_print)   
        self.Bind(wx.EVT_BUTTON, self.OnPause, self.button_pause)   
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.button_cancel)   
        
        self.Bind(wx.EVT_BUTTON, self.On_Refresh_file, self.button_refresh_file) 
        self.Bind(wx.EVT_BUTTON, self.On_SD_Init, self.button_init_sd) 
        self.Bind(wx.EVT_BUTTON, self.On_SD_eject_sd, self.button_eject_sd)     
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnFileListCtrlItemSelected, self.list_ctrl_local_file)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSDFileListCtrlItemSelected, self.list_ctrl_sd_file)
        
        pass
    
    def OnSDFileListCtrlItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        print("OnItemSelected: %s, %s\n" %
              (self.currentItem,
               self.list_ctrl_sd_file.GetItemText(self.currentItem)                            
               ))
        if self._oct_conn.is_operational():    
            self._cur_sel_file = self.list_ctrl_sd_file.GetItemText(self.currentItem)
            self._cur_sel_file_orign = "fbotSdcard"        
            self.label_file.SetLabel(self._cur_sel_file)    
                    
        
    def OnFileListCtrlItemSelected(self, event):
        ##print event.GetItem().GetTextColour()
        self.currentItem = event.m_itemIndex
        print("OnItemSelected: %s, %s\n" %
                           (self.currentItem,
                            self.list_ctrl_local_file.GetItemText(self.currentItem)                            
                            ))
        if self._oct_conn.is_operational():    
            self._cur_sel_file = self.list_ctrl_local_file.GetItemText(self.currentItem)
            self._cur_sel_file_orign = "local"            
            self.label_file.SetLabel(self._cur_sel_file)  
        '''
        def select_file_fun(app, args_none):
            app._oct_file.command("select", target='local', filename=self.list_ctrl_local_file.GetItemText(self.currentItem))            
        self._async_octoprint_api(select_file_fun)           
        '''
        #if self.currentItem == 10:
        #    print("OnItemSelected: Veto'd selection\n")            
        #    self.list_ctrl_local_file.SetItemState(10, 0, wx.LIST_STATE_SELECTED)
        #event.Skip()
        
        
        
    def InitLoadData(self):
        self.list_ctrl_local_file.InsertColumn(0, "Name", wx.LIST_FORMAT_LEFT)
        self.list_ctrl_local_file.InsertColumn(1, "Size", wx.LIST_FORMAT_RIGHT)
        self.list_ctrl_sd_file.InsertColumn(0, "Name", wx.LIST_FORMAT_LEFT)
        self.list_ctrl_sd_file.InsertColumn(1, "Size", wx.LIST_FORMAT_RIGHT)        
    
        self._oct_conn = Connection_api()
        self._oct_job = Job_api()
        self._oct_file = File_api()     
        self._oct_printer = Print_api()     

        #self.UpdateUIFollowConnectOrDis(None, None)
        
        self._update_thread = UpdateThread(self, self._oct_conn, self._oct_printer, self._oct_job)
        self._update_thread.Start()
        self.Bind(EVT_UPDATE_UI, self.OnUpdate)
        
        self.updatefile()
        
        '''  
            cb = wx.ComboBox(self, 500, "default value", (90, 50), 
                             (160, -1), sampleList,
                             wx.CB_DROPDOWN
                             #| wx.TE_PROCESS_ENTER
                             #| wx.CB_SORT
                             )
            cb.SetSelection(0)
            cb.GetValue()
         '''
               
        pass
    
    def _UpdateListCtrlFiles(self, listctrl, datas):
        '''datas = [
            ("file-xxx1", "1123"),
            ("file-xxx2", "3134234")]        
       '''
        listctrl.DeleteAllItems()
        
        if datas is None:
            return 
        else :
            for d in datas:
                index = listctrl.InsertStringItem(sys.maxint, d[0])
                size_str = float(d[1])
                if size_str > 1048576:  #1M = 1048576= 1024 * 1024
                    size_str = "{:.1f}".format(size_str /1048576) + "M"
                elif size_str > 1024:  #1024 
                    size_str = "{:.1f}".format(size_str /1024) + "K"   
                else :
                    size_str = "{:.1f}".format(size_str) 
                listctrl.SetStringItem(index, 1, size_str)                 
        listctrl.SetColumnWidth(0, 330)
        listctrl.SetColumnWidth(1, 95)    
        
    def _async_octoprint_api(self, call_func):
        thread_file = threading.Thread(target=call_func, args=(self, None))
        thread_file.daemon = True
        thread_file.start()        
    
    
    def updatefile(self, local=None):        
        def _update_local_file(app, args_none):
            '''if app._oct_conn.is_closed():
                print("update file close")
                evt = UpdateUIEvent(listctrl=app.list_ctrl_local_file, list_datas=None)
                wx.PostEvent(app, evt)  
                evt = UpdateUIEvent(listctrl=app.list_ctrl_local_sd, list_datas=None)
                wx.PostEvent(app, evt)                  
            else:
            '''
            print("_update_local_file")
            files = []
            file_infos = app._oct_file.get_local_file()
            if file_infos is not None:
                for f in file_infos:
                    files.append(f.get_file_alldata())
                print("files:%s" % files)
            evt = UpdateUIEvent(listctrl=app.list_ctrl_local_file, list_datas=files)
            wx.PostEvent(app, evt)
            
        def _update_sd_file(app, args_none):
            print("_update_sd_file")         
            files = []
            file_infos = app._oct_file.get_sd_file()
            if file_infos is not None:
                for f in file_infos:
                    files.append(f.get_file_alldata())
                print("files sd:%s" % files)
            evt = UpdateUIEvent(listctrl=app.list_ctrl_sd_file, list_datas=files)
            wx.PostEvent(app, evt)     
        if local is not None and 'sd' in local:
            self._async_octoprint_api(_update_sd_file)
        elif local is not None and 'local' in local:
            self._async_octoprint_api(_update_local_file)
        else:
            self._async_octoprint_api(_update_local_file)            
            self._async_octoprint_api(_update_sd_file)
    
    def UpdateUIFollowConnectOrDis(self, args_none1, args_none2): #args_none1 for thread
        #self._oct_conn.get_connection_info() 
        all_profile = self._oct_conn.get_connection_all_printerProfile()                       
        self.combo_box_profile.Clear()
        self.combo_box_profile.AppendItems(all_profile)  
        
        self.button_connect.Enable(True)
        
        if self._oct_conn.is_closed():     
            self.combo_box_profile.Enable(True)  
            self.combo_box_profile.SetSelection(0)
            self.button_connect.SetLabel("Connect")                        
        else :
            cur_profile = self._oct_conn.get_connection_printerProfile()
            set_id = 0
            for p in all_profile:                
                if cur_profile == p:
                    break
                set_id += 1
            self.combo_box_profile.SetSelection(set_id)
            self.combo_box_profile.Enable(False)
            self.button_connect.SetLabel("Disconnect")
            
        
        self.UpdateUIFollowState(self._oct_conn.get_connection_state())
    
    def UpdateUIFollowState(self, status):
        
        self.label_status.SetLabel(status)
        
        if "error" in status:
            self.combo_box_profile.Enable(True)
            self.button_connect.SetLabel("Connect")      
            
            self.button_print.Enable(False)
            self.button_pause.Enable(False)
            self.button_cancel.Enable(False)            

            pass
        elif "Closed" in status:
            self.combo_box_profile.Enable(True)
            self.button_connect.SetLabel("Connect")   
            self.button_print.Enable(False)
            self.button_pause.Enable(False)
            self.button_cancel.Enable(False)            
            pass        
        elif "Operational" in status:            
            self.button_print.Enable(True)
            self.button_pause.SetLabel("Pause")
            self.button_pause.Enable(False)
            self.button_cancel.Enable(False)            
            pass
        elif "Printing" in status:            
            self.button_print.Enable(False)
            self.button_pause.SetLabel("Pause")
            self.button_pause.Enable(True)
            self.button_cancel.Enable(True)             
            pass
        elif "Paused" in status:               
            self.button_print.Enable(False)
            self.button_pause.SetLabel("Resume")
            self.button_pause.Enable(True)
            self.button_cancel.Enable(True)             
            pass
        
        print("UpdateUIFollowState status:%s" % str(status))
        
    def _covert_time(self, second):
        sec_str = 0
        if second is not None or not second or second != 'None':
            sec_str = float(second)
            if sec_str > 3600:  #1hour = 3600 = 60 * 60 
                sec_str = "{:.1f}".format(sec_str /3600) + " Hour"
            elif sec_str > 60:  #60
                sec_str = "{:.1f}".format(sec_str /60) + " Min"   
            else :
                sec_str = "{:.0f}".format(sec_str) + " Second"          
        
        return sec_str
        
    #all UI update
    def OnUpdate(self, evt):
        #evt = UpdateUIEvent(bed_text=bed_text, tool_text=tool_text, status_change=status_change, value = 1)
        #print("onUpdate, bar:%s, val=%s" % (str(evt.bed_text), str(evt.tool_text)), str(evt.status_change))
        if hasattr(evt, 'bed_text'):
            self.label_bed.SetLabel(evt.bed_text)
        if hasattr(evt, 'tool_text'):            
            self.label_ext1.SetLabel(evt.tool_text[0])
            self.label_ext2.SetLabel(evt.tool_text[1])
            self.label_ext3.SetLabel(evt.tool_text[2])

        if hasattr(evt, 'total_time'):             
            self.label_total_time.SetLabel(self._covert_time(evt.total_time)) 
            self.label_print_time.SetLabel(self._covert_time(evt.print_time)) 
            self.label_print_left.SetLabel(self._covert_time(evt.print_left))   
            
        if hasattr(evt, 'status_change') and evt.status_change:
            self.UpdateUIFollowConnectOrDis(None, None)
            

        if hasattr(evt, 'listctrl'):
            self._UpdateListCtrlFiles(evt.listctrl, evt.list_datas)
        pass   
    
    def OnSelectProfile(self, event):
        print("OnSelectProfile event:%s" % str(self.combo_box_profile.GetValue()))
        pass
    
    def OnConnectOrDisconnect(self, event):
        print("OnConnectOrDisconnect")
        if self.button_connect.GetLabel() == "Disconnect":     
            print("OnConnectOrDisconnect, Disconnect")
            def disconnect_fun(app, args_none):
                app._oct_conn.command(command="disconnect")                  
                #self._async_octoprint_api(self.UpdateUIFollowConnectOrDis)
                self.updatefile('local')                
            self._async_octoprint_api(disconnect_fun)            
        else :
            print("OnConnectOrDisconnect, Connect")
            def connect_fun(app, args_none):
                app._oct_conn.command(command="connect", autoconnect=False, baudrate=115200, port="AUTO", printerProfile=self.combo_box_profile.GetValue())
                #self._async_octoprint_api(self.UpdateUIFollowConnectOrDis)
                self.updatefile('local')                
            self._async_octoprint_api(connect_fun)             
            
        self.button_connect.Enable(False)
        #self.UpdateUIFollowConnectOrDis() 
        
        #self._async_octoprint_api(self.UpdateUIFollowConnectOrDis)
        #self.updatefile()
    
    def OnPrint(self, event):
        print("print start")
        def print_fun(app, args_none):
            filename = self._cur_sel_file
            if filename is None or filename == "":
                return
            app._oct_file.command("select", target=self._cur_sel_file_orign, filename=filename)                
            app._oct_job.command("start")                   
        self._async_octoprint_api(print_fun)
               
        pass
    
    def OnPause(self, event):
        print("print pause")  
        if self.button_pause.GetLabel() == "Pause":   
            def pause_fun(app, args_none):
                app._oct_job.command("pause")            
            self._async_octoprint_api(pause_fun)       
        elif self.button_pause.GetLabel() == "Resume":  
            def resume_fun(app, args_none):
                app._oct_job.command("restart")            
            self._async_octoprint_api(resume_fun)
        self.button_pause.Enable(False)
           
    def OnCancel(self, event):
        print("print cancel")
        def cancel_fun(app, args_none):
            app._oct_job.command("cancel")            
        self._async_octoprint_api(cancel_fun)                 
        pass           
    
    def On_Refresh_file(self, event):
        def sd_refresh_fun(app, args_none):
            app._oct_printer.sd_init_eject("refresh")            
        self._async_octoprint_api(sd_refresh_fun)         
        self.updatefile()                
    
    def On_SD_Init(self, event):
        print("On_SD_Init")
        def sd_init_fun(app, args_none):
            app._oct_printer.sd_init_eject("init")            
        self._async_octoprint_api(sd_init_fun)                  
        
    def On_SD_eject_sd(self, event):
        print("On_SD_eject")
        def sd_init_fun(app, args_none):
            app._oct_printer.sd_init_eject("release") 
            app.updatefile('sd')
        self._async_octoprint_api(sd_init_fun)          
        pass    
            
class UpdateThread:
    def __init__(self, win, conn, printer, job):
        self.win = win
        self._oct_conn = conn 
        self._oct_printer = printer 
        self._oct_job = job 
        
    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        last_printer_status = "unknown"
        
        while self.keepGoing:
            bed_text = "off"
            tool_text = ["off", "off", "off"]            
            total_time = "0"
            print_time = "0"
            print_left = "0"
            
            self._oct_conn.get_connection_info()    
            current_status = self._oct_conn.get_connection_state()
            if current_status != last_printer_status:
                status_change = True
                last_printer_status = current_status                                     
            else:
                status_change = False
            
            if not self._oct_conn.is_closed():
                #get temp, 
                bed_temp = self._oct_printer.get_bed_temp()
                if bed_temp is not None and 'bed' in  bed_temp:
                    bed_text = str(bed_temp["bed"]["actual"]) + " : "  + str(bed_temp["bed"]["target"])
                    
                tool_temp = self._oct_printer.get_tool_temp()
                if tool_temp is not None:
                    tool_text = []
                    if "tool0" in tool_temp  and "tool0" in tool_temp:
                        x = tool_temp["tool0"]["actual"]  + " : "  +  tool_temp["tool0"]["target"]           
                        tool_text.append(x)
                    else:
                        tool_text.append("off")
                    if "tool1" in tool_temp  and "tool1" in tool_temp:
                        x = str(tool_temp["tool1"]["actual"]) + " : "  + str(tool_temp["tool1"]["target"])  
                        tool_text.append(x)                            
                    else:
                        tool_text.append("off")                        
                    if "tool2" in tool_temp  and "tool2" in tool_temp:
                        x = str(tool_temp["tool2"]["actual"]) + " : "  + str(tool_temp["tool2"]["target"])  
                        tool_text.append(x)                            
                    else:
                        tool_text.append("off")   
                        
                if self._oct_conn.is_printing() or self._oct_conn.is_pause():
                #{'estimatedPrintTime':self._job['estimatedPrintTime'], 'printTime':self._progress['printTime'], 'printTimeLeft':self._progress['printTimeLeft']}
                    job = self._oct_job.get_job_state()      
                    total_time = job["estimatedPrintTime"]
                    print_time = job["printTime"]
                    print_left = job["printTimeLeft"]
            if print_time == "0":
                evt = UpdateUIEvent(bed_text=bed_text, tool_text=tool_text, status_change=status_change)            
            else :
                evt = UpdateUIEvent(bed_text=bed_text, tool_text=tool_text, status_change=status_change, 
                                total_time=total_time, print_time=print_time, print_left=print_left)
            wx.PostEvent(self.win, evt)             
            time.sleep(2)

        self.running = False

    
if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()