# -*- coding: utf-8 -*-
import os
import re
from tempfile import mkdtemp
import subprocess
import shutil


class PythonROUGE:
  MODEL_IDS = ["A", "B", "C", "D", "E", "F", "G"]

  def __init__(self,
               ROUGE_path="",
               data_path="",
               n_gram=2,
               ROUGE_SU4=True,
               ROUGE_L=False,
               ROUGE_W=False,
               ROUGE_W_Weight=1.2,
               stemming=True,
               stopwords=False,
               word_level=True,
               length_limit=True,
               length=100,
               use_cf=False,
               cf=95,
               scoring_formula="average",
               resampling=True,
               samples=1000,
               favor=True,
               p=0.5):
    """
    Parameters:
        ROUGE_path: absolute path of ROUGE-RELEASE-1.5.5 installation.
        data_path: absolute data path of ROUGE-RELEASE-1.5.5 installation.
        n_gram: Compute ROUGE-N up to max-ngram length will be computed.
        ROUGE_SU4: Compute ROUGE-SU4 measures unigram and skip-bigram
        separated by up to four words.
        ROUGE_L: Calculate ROUGE-L.
        stemming: Stem both model and system summaries using Porter stemmer before computing various statistics.
        stopwords: Remove stopwords in model and system summaries before computing various statistics.
        word_level: Evaluate based on words. If False, rouge evaluates the system summary based on bytes.
        length_limit: If you want to limit the length of the system summary, set True.
        length: Limit first N words/bytes of the system summary.
        use_cf: If True, you can use confidence interval to compute.
        cf: Confidence interval (default is 95%)
        scoring_formula: 'average' is calculated by model average. 'best' is calculated by best model.
        resampling: Use bootstrap resampling.
        samples: pecify the number of sampling point in bootstrap resampling (default is 1000).
        favor: If True, set relative importance of ROUGE scores as blow.
        p: Relative importance of recall and precision ROUGE scores. Alpha -> 1 favors precision, Alpha -> 0 favors recall.
    """
    if ROUGE_path:
      self.ROUGE_path = ROUGE_path
    else:
      raise ValueError("ROUGE_path must be specified.")

    if data_path:
      self.data_path = data_path
    else:
      raise ValueError("data_path must be specified.")

    self.n_gram = n_gram
    self.ROUGE_SU4 = ROUGE_SU4
    self.ROUGE_L = ROUGE_L
    self.ROUGE_W = ROUGE_W
    self.ROUGE_W_Weight = ROUGE_W_Weight
    self.stemming = stemming
    self.stopwords = stopwords
    self.length_limit = length_limit
    self.length = length
    self.word_level = word_level
    self.use_cf = use_cf
    self.cf = cf
    self.scoring_formula = scoring_formula
    self.resampling = resampling
    self.samples = samples
    self.favor = favor
    self.p = p

    self.rouge_cmd_tmp = self._get_rouge_cmd()  # command template

  def _get_rouge_cmd(self):
    ROUGE_path = os.path.abspath(self.ROUGE_path)
    data_path = os.path.abspath(self.data_path)

    rouge_cmd = ['perl', ROUGE_path, "-e", data_path, "-a"]
    assert self.n_gram > 0, "n-gram should be positive."
    rouge_cmd += "-n {}".format(self.n_gram).split()

    if self.ROUGE_SU4:
      rouge_cmd += "-2 4 -u".split()
    if not self.ROUGE_L:
      rouge_cmd.append("-x")
    if self.ROUGE_W:
      rouge_cmd.append("-w")
      rouge_cmd.append(str(self.ROUGE_W_Weight))
    if self.length_limit:
      assert self.length > 0, "Length limit should be positive."
      if self.word_level:
        rouge_cmd += "-l {}".format(self.length).split()
      else:
        rouge_cmd += "-b {}".format(self.length).split()
    if self.stemming:
      rouge_cmd.append("-m")
    if self.stopwords:
      rouge_cmd.append("-s")
    if self.use_cf:
      rouge_cmd += "-c {}".format(self.cf).split()

    if self.scoring_formula == "average":
      rouge_cmd += "-f A".split()
    elif self.scoring_formula:
      rouge_cmd += "-f B".split()
    else:
      raise ValueError("Choose scoring formula between 'average' and 'best'.")

    if self.resampling:
      rouge_cmd += "-r {}".format(self.samples).split()
    if self.favor:
      rouge_cmd += "-p {}".format(self.p).split()

    return rouge_cmd

  def convert_and_config(self, summary=[], reference=[], output_dir=""):
    """
    Convert summaries and references to ROUGE format and generate config file.

    Parameters:
        summary: triple list
          Exmaple: summary = [[[summaryA_model1_sent1, summaryA_model1_sent2],
                               [summaryA_model2_sent1, summaryA_model2_sent2]],
                              [[summaryB_model1_sent1, summaryB_model1_sent2],
                               [summaryB_model2_sent1, summaryB_model2_sent2]]]
        reference: triple list
          Example: reference = [[[summaryA_ref1_sent1, summaryA_ref1_sent2],
                                 [summaryA_ref2_sent1, summaryA_ref2_sent2]],
                                [[summaryB_ref1_sent1, summaryB_ref1_sent2],
                                 [summaryB_ref2_sent1, summaryB_ref2_sent2]]]
        output_dir: directory of outputs. Temp dir is created if not given.

    """
    assert len(summary) == len(
        reference), "Size of summary and refernece is different."
    if not output_dir:
      output_dir = mkdtemp()
    elif not os.path.exists(output_dir):
      os.mkdir(output_dir)

    # Save system and reference files in output_dir
    summary_path = os.path.join(output_dir, "system")
    reference_path = os.path.join(output_dir, "reference")
    os.mkdir(summary_path)
    os.mkdir(reference_path)

    sum_file_lists = []
    for i, sums in enumerate(summary):
      file_list = []
      for j, sents in enumerate(sums):
        filename = "{}_{}.txt".format(i, j)
        with open(os.path.join(summary_path, filename), "w") as f:
          f.writelines("\n".join(sents) + "\n")
        file_list.append(filename)
      sum_file_lists.append(file_list)

    ref_file_lists = []
    for i, refs in enumerate(reference):
      file_list = []
      for j, sents in enumerate(refs):
        filename = "{}_{}.txt".format(i, j)
        with open(os.path.join(reference_path, filename), "w") as f:
          f.writelines("\n".join(sents) + "\n")
        file_list.append(filename)
      ref_file_lists.append(file_list)

    config_path = os.path.join(output_dir, "config.xml")
    with open(config_path, "w") as xml_file:
      config_str = '<ROUGE-EVAL version="1.0">\n'

      for i, (sum_fl, ref_fl) in enumerate(zip(sum_file_lists, ref_file_lists)):
        config_str += '<EVAL ID="{}">\n'.format(i + 1)
        config_str += "<PEER-ROOT>{}</PEER-ROOT>\n".format(summary_path)
        config_str += "<MODEL-ROOT>{}</MODEL-ROOT>\n".format(reference_path)
        config_str += '<INPUT-FORMAT TYPE="SPL">\n"</INPUT-FORMAT>\n'

        config_str += "<PEERS>\n"
        for j, fn in enumerate(sum_fl):
          config_str += '<P ID="{}">{}</P>\n'.format(j + 1, fn)  # start with 1
        config_str += "</PEERS>\n"

        config_str += "<MODELS>\n"
        for j, fn in enumerate(ref_fl):
          config_str += '<M ID="{}">{}</M>\n'.format(self.MODEL_IDS[j], fn)
        config_str += "</MODELS>\n"
        config_str += "</EVAL>\n"

      config_str += "</ROUGE-EVAL>\n"
      xml_file.write(config_str)

    return output_dir, config_path

  def run_rouge(self, config_path):
    rouge_cmd = self.rouge_cmd_tmp + [config_path]
    output = subprocess.check_output(rouge_cmd, stderr=subprocess.STDOUT)
    return output

  def output_to_dict(self, output, recall_only=False, f_measure_only=False):
    """ Convert ROUGE output to key-value pairs in a dictionary. """
    assert not (
        recall_only and f_measure_only
    ), "At least one of recall_only and f_measure_only must be False."

    output = output.decode("utf-8")
    outputs = output.strip().split("\n")
    result = dict()
    n = 1
    for line in outputs:
      if self.ROUGE_SU4:
        su_r_match = re.findall('A ROUGE-SU4 Average_R: ([0-9.]+)', line)
        su_p_match = re.findall('A ROUGE-SU4 Average_P: ([0-9.]+)', line)
        su_f_match = re.findall('A ROUGE-SU4 Average_F: ([0-9.]+)', line)
        if su_r_match:
          if recall_only:
            result['ROUGE-SU4'] = float(su_r_match[0])
          elif f_measure_only:
            pass
          else:
            result['ROUGE-SU4-R'] = float(su_r_match[0])
        if not recall_only:
          if f_measure_only and su_f_match:
            result['ROUGE-SU4'] = float(su_f_match[0])
          else:
            if su_p_match and not f_measure_only:
              result['ROUGE-SU4-P'] = float(su_p_match[0])
            elif su_f_match and not f_measure_only:
              result['ROUGE-SU4-F'] = float(su_f_match[0])
      if self.ROUGE_L:
        l_r_match = re.findall('A ROUGE-L Average_R: ([0-9.]+)', line)
        l_p_match = re.findall('A ROUGE-L Average_P: ([0-9.]+)', line)
        l_f_match = re.findall('A ROUGE-L Average_F: ([0-9.]+)', line)
        if l_r_match:
          if recall_only:
            result['ROUGE-L'] = float(l_r_match[0])
          elif f_measure_only:
            pass
          else:
            result['ROUGE-L-R'] = float(l_r_match[0])
        if not recall_only:
          if f_measure_only and l_f_match:
            result['ROUGE-L'] = float(l_f_match[0])
          else:
            if l_p_match and not f_measure_only:
              result['ROUGE-L-P'] = float(l_p_match[0])
            elif l_f_match and not f_measure_only:
              result['ROUGE-L-F'] = float(l_f_match[0])
      if self.ROUGE_W:
        w_r_match = re.findall(
            'A ROUGE-W-{} Average_R: ([0-9.]+)'.format(self.ROUGE_W_Weight),
            line)
        w_p_match = re.findall(
            'A ROUGE-W-{} Average_P: ([0-9.]+)'.format(self.ROUGE_W_Weight),
            line)
        w_f_match = re.findall(
            'A ROUGE-W-{} Average_F: ([0-9.]+)'.format(self.ROUGE_W_Weight),
            line)
        if w_r_match:
          if recall_only:
            result['ROUGE-W-{}'.format(self.ROUGE_W_Weight)] = float(
                w_r_match[0])
          elif f_measure_only:
            pass
          else:
            result['ROUGE-W-{}-R'.format(self.ROUGE_W_Weight)] = float(
                w_r_match[0])
        if not recall_only:
          if f_measure_only and w_f_match:
            result['ROUGE-W-{}'.format(self.ROUGE_W_Weight)] = float(
                w_f_match[0])
          else:
            if w_p_match and not f_measure_only:
              result['ROUGE-W-{}-P'.format(self.ROUGE_W_Weight)] = float(
                  w_p_match[0])
            elif w_f_match and not f_measure_only:
              result['ROUGE-W-{}-F'.format(self.ROUGE_W_Weight)] = float(
                  w_f_match[0])
      r_match = re.findall('A ROUGE-{} Average_R: ([0-9.]+)'.format(n), line)
      p_match = re.findall('A ROUGE-{} Average_P: ([0-9.]+)'.format(n), line)
      f_match = re.findall('A ROUGE-{} Average_F: ([0-9.]+)'.format(n), line)
      if r_match:
        if recall_only:
          result['ROUGE-{}'.format(n)] = float(r_match[0])
        elif f_measure_only:
          pass
        else:
          result['ROUGE-{}-R'.format(n)] = float(r_match[0])
      if not recall_only:
        if f_measure_only and f_match:
          result['ROUGE-{}'.format(n)] = float(f_match[0])
        else:
          if p_match and not f_measure_only:
            result['ROUGE-{}-P'.format(n)] = float(p_match[0])
          elif f_match and not f_measure_only:
            result['ROUGE-{}-F'.format(n)] = float(f_match[0])
      if f_match: n += 1

    return result

  def evaluate(self, summary, reference, to_dict=False):
    """
    Parameters:
      summary: triple list.
      reference: triple list.
      to_dict: True if results need to be converted to dictionary.
    """
    output_dir, config_path = self.convert_and_config(summary, reference)
    result = self.run_rouge(config_path)
    shutil.rmtree(output_dir)

    if to_dict:
      result = self.output_to_dict(result)

    return result
