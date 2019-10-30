import output_devourer
import time

if __name__ == '__main__':
    dev = output_devourer.spawn('cat /Users/bobizma/Downloads/google-cloud-dataproc-metainfo_d3fbd296-56f0-499c-89cc-4944f6b56356_hive-cluster-m_dataproc-initialization-script-0_output; sleep 7; echo pizdets')
    time.sleep(8.0)
    dev.finalize()
    print(dev.message)
