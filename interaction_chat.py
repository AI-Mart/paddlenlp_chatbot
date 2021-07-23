# -*- coding: utf-8 -*-
"""
@Author  :Mart
@Time    :2021/7/8 21:25
@version :Python3.7.4
@Software:pycharm2020.3.2
"""
import re
import argparse
from termcolor import colored, cprint
from paddlenlp.transformers import (UnifiedTransformerLMHeadModel,
                                    UnifiedTransformerTokenizer)
from utils import set_seed, select_response
from collections import deque


def parse_args():
    """
    pass
    """
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--model_name_or_path', type=str, default='plato-mini',
                        help='The path or shortcut name of the pre-trained model.')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for initialization.')
    parser.add_argument('--min_dec_len', type=int, default=1, help='The minimum sequence length of generation.')
    parser.add_argument('--max_dec_len', type=int, default=64, help='The maximum sequence length of generation.')
    parser.add_argument('--num_return_sequences', type=int, default=20,
                        help='The numbers of returned sequences for one input in generation.')
    parser.add_argument('--decode_strategy', type=str, default='sampling', help='The decode strategy in generation.')
    parser.add_argument('--top_k', type=int, default=5,
                        help='The number of highest probability vocabulary tokens to keep for top-k sampling.')
    parser.add_argument('--temperature', type=float, default=1.0,
                        help='The value used to module the next token probabilities.')
    parser.add_argument('--top_p', type=float, default=1.0, help='The cumulative probability for top-p sampling.')
    parser.add_argument('--num_beams', type=int, default=0, help='The number of beams for beam search.')
    parser.add_argument('--length_penalty', type=float, default=1.0,
                        help='The exponential penalty to the sequence length for beam search.')
    parser.add_argument('--early_stopping', type=eval, default=False,
                        help='Whether to stop the beam search when at least `num_beams` '
                             'sentences are finished per batch or not.')
    parser.add_argument('--device', type=str, default='cpu', help='The device to select for training the model.')

    args_ = parser.parse_args()
    return args_


args = parse_args()

# model.generate  D:\Program Files\Python37\Lib\site-packages\paddlenlp\transformers\generation_utils.py


class PlatoNlp(object):
    """
    pass
    """
    def __init__(self, max_turn=5):
        if args.seed is not None:
            set_seed(args.seed)
        # Initialize the model and tokenizer
        self.model = UnifiedTransformerLMHeadModel.from_pretrained(
            args.model_name_or_path)
        self.tokenizer = UnifiedTransformerTokenizer.from_pretrained(
            args.model_name_or_path)

        self.model.eval()
        self.history = deque(maxlen=max_turn)

    def predict(self, data):
        """
        pass
        """
        data = re.sub(r'\s', '', data)
        self.history.append(data)
        inputs = self.tokenizer.dialogue_encode(
            list(self.history),
            add_start_token_as_response=True,
            return_tensors=True,
            is_split_into_words=False)
        inputs['input_ids'] = inputs['input_ids'].astype('int64')
        ids, scores = self.model.generate(
            input_ids=inputs['input_ids'],
            token_type_ids=inputs['token_type_ids'],
            position_ids=inputs['position_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=args.max_dec_len,
            min_length=args.min_dec_len,
            decode_strategy=args.decode_strategy,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            num_beams=args.num_beams,
            length_penalty=args.length_penalty,
            early_stopping=args.early_stopping,
            num_return_sequences=args.num_return_sequences)
        bot_response = select_response(
            ids,
            scores,
            self.tokenizer,
            args.max_dec_len,
            args.num_return_sequences,
            keep_space=False)[0]
        self.history.append(bot_response)
        return bot_response


if __name__ == '__main__':
    PlatoNlpR = PlatoNlp()
    start_info = "Enter [EXIT] to quit the interaction, [NEXT] to start a new conversation."
    cprint(start_info, "yellow", attrs=["bold"])
    while True:
        user_utt_ = input(colored("[Human]: ", "red", attrs=["bold"])).strip()
        if user_utt_ == "[EXIT]":
            break
        elif user_utt_ == "[NEXT]":
            PlatoNlpR.history.clear()
            cprint(start_info, "yellow", attrs=["bold"])
        bot_response_ = PlatoNlpR.predict(user_utt_)
        print(
            colored(
                "[Bot]:", "blue", attrs=["bold"]),
            colored(
                bot_response_, attrs=["bold"]))

