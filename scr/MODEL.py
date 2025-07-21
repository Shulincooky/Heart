import torch
import torch.nn as nn
from typing import Optional, Tuple

class EmotionGRU(nn.Module):
    """
    情绪生成模型
    ---------------
    输入张量均按 (batch, seq_len, feat) 排布，除 hidden_state 外。
    forward 返回 (E_t, h_n)
      • E_t : (batch, seq_len, 7)    — 每步情绪权重 ∈ [0,1]
      • h_n : (num_layers, batch, hidden)
    """
    def __init__(
        self,
        personality_embed_dim: int = 16,   # 5 维 OCEAN → P_e
        input_fc_dim: int = 64,
        gru_hidden: int = 128,
        gru_layers: int = 2,
        dropout: float = 0.2
    ) -> None:
        super().__init__()

        # 1) 人格嵌入层 5 → P_e
        self.p_embed = nn.Linear(5, personality_embed_dim)

        # 2) 计算拼接特征总维度（除人格外的 24 维固定部分）
        self.base_feat_dim = 24                        # ΔE7 + gate1 + time2 + holiday1 + weather5 + temp1 + E_prev7 = 24
        in_dim = self.base_feat_dim + personality_embed_dim

        # 3) 输入映射 & GRU
        self.input_fc = nn.Sequential(
            nn.Linear(in_dim, input_fc_dim),
            nn.ReLU()
        )
        self.gru = nn.GRU(
            input_fc_dim,
            gru_hidden,
            num_layers=gru_layers,
            batch_first=True,
            dropout=dropout if gru_layers > 1 else 0.0
        )

        # 4) 输出层：hidden → 7 (Sigmoid)
        self.out_fc = nn.Linear(gru_hidden, 7)
        self.activation = nn.Sigmoid()

    # -----------------------------------------------------------------
    def forward(
        self,
        prev_emotion: torch.Tensor,  # (B,S,7)
        deltaE: torch.Tensor,        # (B,S,7)
        gate: torch.Tensor,          # (B,S,1)
        time_enc: torch.Tensor,      # (B,S,2)
        holiday: torch.Tensor,       # (B,S,1)
        weather: torch.Tensor,       # (B,S,5)
        temp: torch.Tensor,          # (B,S,1)
        personality: torch.Tensor,   # (B,5)
        hidden: Optional[torch.Tensor] = None  # (L,B,H)
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        将全部特征拼接后送入 GRU进行预测打分
        ---------------
        prev_emotion 上一时刻的7维情感状态
        deltaE LLM为对方语言分析合成后的打分
        gate deltaE 的门控开关（0=忽略变化，1=应用变化）
        time_enc 周期性时间编码（sin/cos形式）
        holiday 距离假期结束时间的打分[0,1]
        weather 天气状况one-hot编码（sunny/cloudy/overcast/rainy/snowy）
        temp 标准化温度值（Z-score归一化）
        personality 用户大五人格特质（OCEAN：开放性/尽责性/外倾性/宜人性/神经质）
        hidden GRU隐藏层状态。默认为零,如果输入则继承隐藏层状态
        """
        # ΔE × gate — 若 gate=0 则清零情绪扰动
        deltaE = deltaE * gate

        # 人格嵌入并广播到序列维
        B, S, _ = prev_emotion.shape
        p_emb = self.p_embed(personality)           # (B,P_e)
        p_emb = p_emb.unsqueeze(1).expand(B, S, -1) # → (B,S,P_e)

        # 按顺序拼接所有特征 (B,S,24+P_e)
        feats = torch.cat(
            [deltaE, gate, time_enc, holiday, weather, temp, prev_emotion, p_emb],
            dim=-1
        )

        # 映射到 GRU 输入维
        x = self.input_fc(feats)                    # (B,S,d_in)

        # 序列递推
        out, h_n = self.gru(x, hidden)              # out:(B,S,H)

        # 逐步预测情绪（若只要最后一步可取 out[:,-1]）
        E_t = self.activation(self.out_fc(out))     # (B,S,7)→[0,1]

        return E_t, h_n
