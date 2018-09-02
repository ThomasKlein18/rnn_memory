import tensorflow as tf
import os

def read_dataset(path, mode, batch_size, num_epochs, seq_length, seq_width, datatype):
    """
    Reads data from .tfrecords-file, decodes it and returns the dataset as a
    tf.data.TFRecordDataset.

    This probably only works for data that was generated using the export_data-script.

    batch_size      int, the batch_size used during training
    num_epochs      int, the number of training epochs
    seq_length      int, the length of the sequences (eg an mnist-image is 784 long)
    seq_width       int, the width of the sequences (dimensionality of the data)
    """

    def _parse_function(example_proto):
        """
        The function that is used to parse the data in the tfrecords-file.
        Both the MNIST-data as well as the AR-data have the column names
        "raw_label" and "raw_sequence", so there is no need for a second parse
        function here.
        If you want to extend this experiment to other datasets, you might need
        to write a different parse function and make read_dataset accept this as
        an argument.
        """
        features = {"raw_sequence": tf.FixedLenFeature([], tf.string, default_value=""),
                    "raw_label": tf.FixedLenFeature([], tf.string, default_value="")}
        parsed_features = tf.parse_single_example(example_proto, features)

        # NOTE: the reason that this will be an int32 is weird and hidden;
        # retrieve sequence
        seq = tf.decode_raw(parsed_features["raw_sequence"], datatype)
        seq.set_shape(seq_length*seq_width)
        seq = tf.reshape(seq, [seq_length, seq_width])
        seq = tf.cast(seq, datatype)

        # retrieve labels [i.e. last and to be predicted element of sequence]
        label = tf.decode_raw(parsed_features["raw_label"], datatype)
        label.set_shape(seq_width)
        label = tf.cast(label, datatype)

        return seq, label

    training_path = os.path.join(path, mode+'.tfrecords')
    training_dataset = tf.data.TFRecordDataset(training_path)
    training_dataset = training_dataset.map(_parse_function)
    training_dataset = training_dataset.batch(batch_size)
    training_dataset = training_dataset.repeat(num_epochs)

    """ validation_path = os.path.join(FLAGS.data_path, 'validation.tfrecords')
    validation_dataset = tf.data.TFRecordDataset(validation_path)
    validation_dataset = validation_dataset.map(_parse_function)
    validation_dataset = validation_dataset.batch(batch_size)
    validation_dataset = validation_dataset.repeat(num_epochs) """

    return training_dataset #, validation_dataset


def input_fn(path, task, config, mode):
    if(task == "mnist"):
        return read_dataset(path, mode, config.batchsize, config.num_epochs, seq_length=784, seq_width=1, datatype=tf.int32)
    elif(task=="associative_retrieval"):
        return read_dataset(path, mode, config.batchsize, config.num_epochs, seq_length=9, seq_width=37, datatype=tf.int32)
    else:
        raise ValueError("Task type not understood.")


def eval_input_fn(path, task, config):
    return input_fn(path, task, config, 'test')


def train_input_fn(path, task, config):
    return input_fn(path, task, config, 'train')
