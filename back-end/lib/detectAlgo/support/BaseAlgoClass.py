from time import time, sleep
import numpy as np
import json

from ...dataBaseEngine import Session
from ...dataBaseEngine import imsBase as DetectModelBase

class BaseModel:
    def __init__(self, index=0, name="model", config={}):
        self.uuid = index
        self.name = name
        self.trainTime = 0
        self.predictTime = -1
        self.multiTrainTime = 0
        self.multiPredictTime = -1
        self.trained = False
        self.set_config(config)

    @property
    def train_state(self):
        return self.trained

    @property
    def train_info(self):
        return [time() - self.trainTime, self.predictTime]

    @property
    def multi_train_info(self): 
        return [time() - self.multiTrainTime, self.multiPredictTime + self.predictTime]

    def get_config(self):
        return self.config

    def set_config(self, config={}):
        self.config = config

    def config_normalization(self, data):
        data = data[~np.isnan(data.sum(axis=-1))]
        self.mins = np.min(data,axis=0)
        self.maxs = np.max(data,axis=0)
        self.id_const = np.where(self.maxs == self.mins)[0]
        self.id_nonconst = np.where(self.maxs != self.mins)[0]

    def reconfig_normalization(self, data):
        data = data[~np.isnan(data.sum(axis=-1))]
        if self.id_const.size:
            mins_ = self.mins[self.id_const]
            maxs_ = self.maxs[self.id_const]
            mins = np.min(data[..., self.id_const],axis=0)
            maxs = np.max(data[..., self.id_const],axis=0)
            mins[mins>mins_] = mins_[mins>mins_]
            maxs[maxs<maxs_] = maxs_[maxs<maxs_]
            min_app = mins_ - mins
            max_app = maxs - maxs_
            min_app[max_app>min_app] = max_app[max_app>min_app]
            self.mins[self.id_const] -= min_app
            self.maxs[self.id_const] += min_app
            self.id_const = np.where(self.maxs == self.mins)[0]
            self.id_nonconst = np.where(self.maxs != self.mins)[0]

    def normalization(self, data):
        for i in self.id_const:
            data_ = data[:,i]
            data_[~np.isnan(data_)] = 0.5 * np.sign(data[~np.isnan(data_), i]-self.mins[i])
            data[:,i] = data_
        for i in self.id_nonconst:
            data_ = data[:,i]
            data_[~np.isnan(data_)] = (data[~np.isnan(data_), i]  - self.mins[i]) / \
                                            (self.maxs[i] - self.mins[i]) - 0.5
            data[:,i] = data_
        return data

    def anti_normalization(self, data):
        data_ = data.copy()
        if self.id_const.size:
            data_[..., self.id_const] += self.mins[self.id_const]
        if self.id_nonconst.size:
            data_[..., self.id_nonconst] = (self.maxs[self.id_nonconst] - self.mins[self.id_nonconst]) * \
                (data_[..., self.id_nonconst] + 0.5)  + self.mins[self.id_nonconst]
        return data_

    def save_model(self, count=0):
        """
        Save Special Configurations
        """
        try:
            config = self.to_json() #long-blob
            obj, relatParas = self.uuid.split("@")
            session = Session()
            session.merge(DetectModelBase(obj=obj, relat_paras=relatParas, model_params=config))
            session.commit()
            session.close()
        except Exception as e:
            if count < 5:
                sleep(1)
                self.save_model(count=count+1)
            else:
                print(f"[ERROR] [{self.name}#{self.uuid}]训练阶段保存失败|{e}")
            
    def load_model(self, uuid=None):
        """
        Load Special Configurations
        """
        if uuid is None:
            uuid = self.uuid
        session = Session()
        obj, relatParas = self.uuid.split("@")
        config = session.query(DetectModelBase.model_params)\
                 .filter(DetectModelBase.obj==obj,
                         DetectModelBase.relat_paras==relatParas).first()
        if config:
            self.from_json(config[0])
            self.trained = True
        else:
            pass
        session.close()

    def to_json(self):
        """
        Load Special Configurations By Path
        """
        return json.dumps(self.config).encode()

    def from_json(self, config=b""):
        """
        Load Special Configurations By Path
        """
        return json.loads(config.decode())

    def fit(self, data, save=True):
        """
        Train Process if Need
        """
        self.trainTime = time()
        self.predictTime = -1

        if not self.trained:
            self.config_normalization(data)
        else:
            self.reconfig_normalization(data)
        X = self.normalization(data)

        if not self.trained:
            pass # Insert your pure training algorithm here
        else:
            pass # Replace your reinforce training algorithm here

        self.trained = True
        if save:
            self.save_model()

    def validate(self, data):
        """
        Input: All Test Data [np.array]
        """
        X = self.normalization(data)

        scores = np.random.uniform(0,1,100) # Replace your validation algorithm here
        
        scores[scores > 1] = 1; scores[scores < 0] = 0
        abList = list(np.where(scores>=0.5)[0])
        return abList, list(scores), [None, None]

    def merged_data(self,data):
        if data[0].ndim == 2:
            data_ = data[0]
            for single_data in data[1:]:
                data_ = np.concatenate((data_,single_data),axis=0)
            return data_
        else:
            return data
