#%%
from flask import Flask, render_template,request
import pandas as pd
import numpy as np

app = Flask(__name__)
#%% 
tissue_dic={"PBMC":"pbmc_db.csv",
            "Heart":"heart_db.csv"}

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        
        # Get the selected dropdown value
        selected_option = request.form.get("dropdown")

        # Get the multi-line input data from the form
        data = request.form.get("user_input")
        
        # Split the data by new lines (rows)
        rows = data.splitlines()

        # Further split each row by commas (for columns)
        data_list = [row.split(',') for row in rows]
        
        # Create a DataFrame from the list of rows
        df = pd.DataFrame(data_list)
        try:
            df.columns=["Chr","Position"]
            df["Chr"]=["chr"+str(i) for i in df["Chr"]  ]
            selected_tissue = str(selected_option)
            df["Tissue type"]=selected_tissue
            df["start"]=[ int(i)-int(i)%5000+1 for i in df["Position"]  ]
            df["end"]=[ int(i)+4999 for i in df["start"]  ]
            df["index-name"]=[df["Chr"][i]+"-"+str(df["start"][i])+"-"+str(df["end"][i]) for i in range(df.shape[0])]
            database = pd.read_csv(f"datasets/{tissue_dic[selected_tissue]}",index_col=0)
            common_sites=np.intersect1d(list(database.index),list(df["index-name"]))
            n_var_input = len(common_sites)
            total_var = df.shape[0]
            n_var_input=str(n_var_input)+" / "+str(total_var)
            ct_sites = database.loc[common_sites,:]
            ct_sites["Celltype"]=ct_sites.idxmax(axis=1)
            df=df.loc[df["index-name"].isin(common_sites)]
            ct_sites=ct_sites.loc[df["index-name"],]
            df = df.loc[:,["Chr","Position","Tissue type"]]
            final_res = df.reset_index(drop=True).join(ct_sites.reset_index(drop=True))
        except:
            return render_template("index.html",err=True)
            

        # Return the DataFrame as HTML
        return render_template("index.html", df=final_res.to_html(classes='table table-bordered'),
                               n_var=n_var_input)
    else:
        return render_template("index.html", df=None)
#%%