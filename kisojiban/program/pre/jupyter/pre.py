import os
import tkinter as tk
import tkinter.filedialog
import datetime
import tkinter.messagebox
from PIL import ImageTk

class Application(tk.Tk):
    def __init__(self):
        global file_path
        self.file_path = ''

        super().__init__()
        # アプリのタイトル
        self.geometry("420x130")
        self.title("[RPFEM解析] .MSH を 2Dyouso.datに変換")
        
        self.tk.call('wm', 'iconphoto', self._w, ImageTk.PhotoImage(file=temp_path('a.jpg')))

        self.create_widgets()

    
    def create_widgets(self):
        self.label1 = tk.Label(self.master, text = "変換前")
        self.label2 = tk.Label(self.master, text = "変換先")
        self.label3 = tk.Label(self.master, text = "説明")

        self.input_box1 = tk.Entry(width=50)
        self.input_box2 = tk.Entry(width=50)
        self.input_box3 = tk.Entry(width=58)
        self.input_box1.insert(0, "result.d を選択してください")
        self.input_box2.insert(0, "")
        self.input_box3.insert(0, datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST')).strftime('%Y/%m/%d %H:%M:%S'))

        self.read_button1 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box1), width=5)
        self.read_button2 = tk.Button(self, text='参照', command=lambda: self.file_select(self.input_box2), width=5)


        label_frame = ttk.Labelframe(frame1, text='Options', padding=(10), style='My.TLabelframe')
        self.radio1_button1 = tk.Radiobutton(label_frame, text='Option A', value='A', variable=v1)
        self.radio1_button2 = tk.Radiobutton(label_frame, text='Option B', value='B', variable=v1)


        self.label1.place(x=5, y=10)
        self.label2.place(x=5, y=40)
        self.label3.place(x=5, y=70)

        self.input_box1.place(x=50, y=10)
        self.input_box2.place(x=50, y=40)
        self.input_box3.place(x=50, y=70)

        self.read_button1.place(x=360, y=10)
        self.read_button2.place(x=360, y=40)

        self.excute_button = tk.Button(self, text="変換", command=lambda: self.file_read(self.input_box1.get(), self.input_box2.get()), width=10)
        self.cancel_button = tk.Button(self, text='閉じる', command=self.quit, width=10)
        self.excute_button.place(x=120, y=100)
        self.cancel_button.place(x=220, y=100)

    def file_select(self, input_box):
        global file_path
        idir = 'C:\\python_test'
        filetype = [("テキストファイル","*.d"), ("テキストファイル","*.dat"), ("テキストファイル","*.txt")]
        file_path = tkinter.filedialog.askopenfilename(filetypes = filetype, initialdir = idir)
        input_box.delete(0, tkinter.END)
        input_box.insert(tkinter.END, file_path)

        if input_box == self.input_box1:
            self.input_box2.delete(0, tkinter.END)
            self.input_box2.insert(tkinter.END, os.path.splitext(file_path)[0]+".dat")
        return file_path

    def file_read(self, path, path_new):
        '読み込みボタンが押された時の処理'
        global lines
        if len(path) == 0:
            tkinter.messagebox.showwarning('確認', 'ファイルが選択されていません')
            return 

        if os.path.basename(path) != 'result.d':
            tkinter.messagebox.showwarning('確認', 'result.d が選択されていません')
            return
        else:
            with open(path, "r", encoding='CP932') as file:
                lines = file.read().splitlines()

            if "計算時間" in lines[-1]:
                file_create(lines, path_new)
                tkinter.messagebox.showinfo('完了', 'ファイルが正しく変換されました')
                self.quit()
            else:
                tkinter.messagebox.showerror('エラー', 'ファイルの中身が正しくありません')
                return

        




    def quit(self):
       self.destroy()

# GUIアプリ生成




def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()