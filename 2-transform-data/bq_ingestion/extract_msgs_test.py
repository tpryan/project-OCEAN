import unittest
import datetime
from dateutil import parser
import extract_msgs as em
import email
import mock
import gzip

class Test(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.ex_binary_post_from_uk = b''.join([
            b'From: UK Parliment <uk.parliment@gmail.com>\n',
            b'To: Emmeline Pankhurst <emmeline.pankhurst@gmail.com>\n',
            b'Subject: Voting Rights\n',
            b'Date: Mon, July 2 1928 13:46:03 +0100\n',
            b'Message-ID:\n',
            b' <voting-rights-id@mail.gmail.com>\n',
            b'MIME-Version: 1.0\n',
            b'Content-Type: text/plain; charset="utf-8"\n',
            b'Content-Transfer-Encoding: 7bit\n',
            b'References: <voting-rights-id@mail.gmail.com>\n',
            b'\n',
            b'Full women voting rights passed in U.K.\n',
            b'\n',
            b'"We are here, not because we are law-breakers; we are here in our efforts to become law-makers."\n'],)
        self.ex_text_post_from_uk = 'From: UK Parliment <uk.parliment@gmail.com>\nTo: Emmeline Pankhurst <emmeline.pankhurst@gmail.com>\nSubject: Voting Rights\nDate: Mon, July 2 1928 13:46:03 +0100\nMessage-ID:\n<voting-rights-id@mail.gmail.com>\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nReferences: <voting-rights-id@mail.gmail.com>\n\nFull women voting rights passed in U.K.\n\n"We are here, not because we are law-breakers; we are here in our efforts to become law-makers."\n'
        self.ex_text_post_from_us1 = 'From: US Congress <us.congress@gmail.com>\nTo: staton.anthony@gmail.com\nSubject: 19th Ammendment\nDate: Wed, Aug 18 1920 11:00:07 +0100\nMessage-ID:\n<19th-ammendment-id@mail.gmail.com>\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nReferences: <19th-ammendment-id@mail.gmail.com>\n\n19th Amemndment ratified in U.S. granting women the right to vote after the final vote in Tennessee.\n\nAs per the Declaration of Sentiments in 1848, "We hold these truths to be self-evident: that all men and women are created equal; that they are endowed by their Creator with certain inalienable rights; that among these are life, liberty, and the pursuit of happiness."\n'
        self.ex_text_post_from_us2 = 'From: US Congress <us.congress@gmail.com>\nTo: ida.b.wells@gmail.com\nSubject: Voter Rights Act\nDate: Wed, Aug 6 1965 15:32:20 +0100\nMessage-ID:\n<voter-rights-act-id@mail.gmail.com>\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nReferences: <voter-rights-act-id@mail.gmail.com>\n\nVoter`s Rights Act outlawed discriminatory voting practices.\n\n  From 1913 suffrage march in DC, "Either I go with you or not at all. I am not taking this stand because I personally wish for recognition. I am doing it for the future benefit of my whole race."\n'
        self.ex_text_post_mime_us1='MIME-Version: 1.0\nSender: us.congress@gmail.com\nReceived: by 10.90.70.10 with HTTP; Wed, Aug 18 1920 11:00:07 -0700 (PDT)\nIn-Reply-To:<voting-rights-id@mail.gmail.com>\nReferences: <19th-ammendment-id@mail.gmail.com>\nFrom: US Congress <us.congress@gmail.com>\nDate: Wed, Aug 18 1920 11:00:07 +0100\nMessage-ID:\n<19th-ammendment-id@mail.gmail.com>\nSubject: 19th Ammendment\nTo: staton.anthony@gmail.com\nContent-Type: text/plain; charset=ISO-8859-1\nContent-Transfer-Encoding: quoted-printable\n\n19th Amemndment ratified in U.S. granting women the right to vote after the final vote in Tennessee.\n\nAs per the Declaration of Sentiments in 1848, "We hold these truths to be self-evident: that all men and women are created equal; that they are endowed by their Creator with certain inalienable rights; that among these are life, liberty, and the pursuit of happiness."\n'
        self.ex_text_post_date_us2='Date: Wed, Aug 6 1965 15:32:20 +0100\nFrom: US Congress <us.congress@gmail.com>\nTo: ida.b.wells@gmail.com\nMessage-ID:\n<voter-rights-act-id@mail.gmail.com>\nSubject: Voter Rights Act\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nReferences: <voter-rights-act-id@mail.gmail.com><ida.b.wells@gmail.com>\n\nVoter`s Rights Act outlawed discriminatory voting practices.\n\n  From 1913 suffrage march in DC, "Either I go with you or not at all. I am not taking this stand because I personally wish for recognition. I am doing it for the future benefit of my whole race."\n'
        self.ex_parsed_msg_single = [[('From', 'UK Parliment <uk.parliment@gmail.com>'),
                          ('To', 'Emmeline Pankhurst <emmeline.pankhurst@gmail.com>'),
                          ('Subject', 'Voting Rights'),
                          ('Date', 'Mon, July 2 1928 13:46:03 +0100'),
                          ('Message-ID', '\n <voting-rights-id@mail.gmail.com>'),
                          ('MIME-Version', '1.0'),
                          ('Content-Type', 'text/plain; charset="utf-8"'),
                          ('Content-Transfer-Encoding', '7bit'),
                          ('References', '<voting-rights-id@mail.gmail.com>'),
                          ("list", "pankhurst-bucket"),
                          ('Body', 'Full women voting rights passed in U.K.\n\n"We are here, not because we are law-breakers; we are here in our efforts to become law-makers."\n')]]
        self.ex_parsed_msg_mult = [[('From', 'US Congress <us.congress@gmail.com>'),
                                    ('To', 'staton.anthony@gmail.com'),
                                    ('Subject', '19th Ammendment'),
                                    ('Date', 'Wed, Aug 18 1920 11:00:07 +0100'),
                                    ('Message-ID', ''), ('list', 'voter-bucket'),
                                    ('Body', '<19th-ammendment-id@mail.gmail.com>\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nReferences: <19th-ammendment-id@mail.gmail.com>\n\n19th Amemndment ratified in U.S. granting women the right to vote after the final vote in Tennessee.\n\nAs per the Declaration of Sentiments in 1848, "We hold these truths to be self-evident: that all men and women are created equal; that they are endowed by their Creator with certain inalienable rights; that among these are life, liberty, and the pursuit of happiness."\n')],
                                   [('From', 'US Congress <us.congress@gmail.com>'),
                                    ('To', 'ida.b.wells@gmail.com'),
                                    ('Subject', 'Voter Rights Act'),
                                    ('Date', 'Wed, Aug 6 1965 15:32:20 +0100'),
                                    ('Message-ID', ''),
                                    ('list', 'voter-bucket'),
                                    ('Body', '<voter-rights-act-id@mail.gmail.com>\nMIME-Version: 1.0\nContent-Type: text/plain; charset="utf-8"\nContent-Transfer-Encoding: 7bit\nReferences: <voter-rights-act-id@mail.gmail.com>\n\nVoter`s Rights Act outlawed discriminatory voting practices.\n\n  From 1913 suffrage march in DC, "Either I go with you or not at all. I am not taking this stand because I personally wish for recognition. I am doing it for the future benefit of my whole race."\n')]]

    # TODO is iso8859 really being tested?
    def test_decode_messsage(self):

        encoded_input = {
            "test1": {
                "comparison_type": "Decode utf8 with from and date",
                "data": b'From ida.b.wells@gmail.com Tue Sep  1 04:14:32 2020\n'
        },
            "test2": {
                "comparison_type": "Decode utf8 with text and special symbols",
                "data": b"Women's Voting Rights.\n"},
            "test3": {"comparison_type":"Decode iso-8859-1",
                      "data": b'\xe0'},
            "test4": {
                "comparison_type":"Decode iso-8859-2",
                "data": b'hello ab\xe4c\xf6'
            },
        }
        want_decode = {
            "test1": 'From ida.b.wells@gmail.com Tue Sep  1 04:14:32 2020\n',
            "test2": "Women's Voting Rights.\n",
            "test3": 'à',
            "test4": 'hello abäcö',
        }

        for key, test in encoded_input.items():
            # print(test['comparison_type'])
            got_decode = em.decode_messsage(test["data"])
            self.assertEqual(want_decode[key], got_decode, "Decode message error")

        #Test passing string error
        test5_input = "Hello New York"
        want_test5 = AttributeError
        self.assertRaises(want_test5, em.decode_messsage, test5_input, "Error raising AttributeError in decode test.")

    # TODO setup test
    def test_decompress_line_by_line(self):
        pass

    @mock.patch("google.cloud.storage.Client")
    @mock.patch("google.cloud.storage.bucket.Bucket")
    @mock.patch("google.cloud.storage.blob.Blob")
    def create_bucket_mock(self, bucket_name, blob_name, content_type, blob_contents,  Blob, Bucket, Client):
        client = Client()

        bucket_mock = Bucket(name=bucket_name)
        blob_mock = Blob(name=blob_name)

        client.get_bucket.return_value = bucket_mock
        bucket_mock.get_blob.return_value = blob_mock

        blob_mock.content_type = content_type
        if 'text/plain' in content_type:
            blob_mock.download_as_text.return_value = blob_contents
        elif 'application/x-gzip' in content_type:
            blob_mock.download_as_bytes.return_value = blob_contents

        return client

    # TODO test for when decode_by_line is triggered and test for errors
    def test_get_msgs_from_gcs(self):

        test_fnames = ['1918-07.txt', '1920-08.mbox.gz', '1965-08.txt.gz']
        test_bucket_names = ['pankhurst-bucket', 'stanton-anthony-golang-announce-bucket', 'wells-bucket']
        test_blob_names = ['uk-rights-blob', 'us-rights-blob', 'us-full-rights-blob']
        test_content_types = ['application/x-gzip', 'text/plain']

        input_gcs = {
            "test1": {
                "comparison_type": "Test single gzip message example with From as the split value",
                "client": self.create_bucket_mock(test_bucket_names[0], test_blob_names[0], test_content_types[0], gzip.compress(self.ex_text_post_from_uk.encode())),
                "bucket_name": test_bucket_names[0],
                "filename": test_fnames[0]
            },
            "test2": {
                "comparison_type": "Test multiple gzip message example with From as the split value",
                "client": self.create_bucket_mock(test_bucket_names[2], test_blob_names[2], test_content_types[0], gzip.compress(self.ex_text_post_from_us1.encode()+self.ex_text_post_from_us2.encode())),
                "bucket_name": test_bucket_names[2],
                "filename": test_fnames[2]
            },
            "test3": {

                "comparison_type": "Test single text message example with MIME as the split value",
                "client": self.create_bucket_mock(test_bucket_names[1], test_blob_names[1], test_content_types[1], self.ex_text_post_mime_us1.encode()),
                "bucket_name": test_bucket_names[1],
                "filename": test_fnames[1]

            },
            "test4": {
                "comparison_type": "Test multiple text message example with MIME as the split value",
                "client": self.create_bucket_mock(test_bucket_names[1], test_blob_names[1], test_content_types[1], self.ex_text_post_mime_us1.encode() + self.ex_text_post_mime_us1.encode()),
                "bucket_name": test_bucket_names[1],
                "filename": test_fnames[1]

            },
            "test5": {
                "comparison_type": "Test single text message example with Date as the split value",
                "client": self.create_bucket_mock(test_bucket_names[2], test_blob_names[2], test_content_types[1], self.ex_text_post_date_us2.encode()),
                "bucket_name": test_bucket_names[2],
                "filename": test_fnames[2]
            },
            "test6": {
                "comparison_type": "Test multiple text message example with Date as the split value",
                "client": self.create_bucket_mock(test_bucket_names[2], test_blob_names[2], test_content_types[1], self.ex_text_post_date_us2.encode()+self.ex_text_post_date_us2.encode()),
                "bucket_name": test_bucket_names[2],
                "filename": test_fnames[2]
            },
            # "test7": {
            #     "comparison_type": "Test UnicodeDecodeError",
            #     "client": self.create_bucket_mock(test_bucket_names[0], test_blob_names[0], test_content_types[0], gzip.compress( b'hello ab\xe4c\xf6')),
            #     "bucket_name": test_bucket_names[0],
            #     "filename": test_fnames[0]
            # },

        }
        want_msg_list = {
            "test1": [self.ex_text_post_from_uk.encode()],
            "test2": [self.ex_text_post_from_us1.encode(), self.ex_text_post_from_us2.encode()],
            "test3": [self.ex_text_post_mime_us1.encode()],
            "test4": [self.ex_text_post_mime_us1.encode(), self.ex_text_post_mime_us1.encode()],
            "test5": [self.ex_text_post_date_us2.encode()],
            "test6": [self.ex_text_post_date_us2.encode(), self.ex_text_post_date_us2.encode()],
            # "test7": Want to test error
        }

        for key, test in input_gcs.items():
            # print(test['comparison_type'])
            got_msg_list= em.get_msgs_from_gcs(test['client'], test['bucket_name'], test['filename'])
            self.assertEqual(want_msg_list[key], got_msg_list, "Get msg from gcs error")


    def test_get_msg_objs_list(self):

        msg_input = {
            "test1": {
                "comparison_type": "Test getting message parts from single message",
                "msgs": [self.ex_binary_post_from_uk],
                "bucketname":"pankhurst-bucket"
            },
            "test2": {
                "comparison_type": "Test getting message parts from multiple messages",
                "msgs":[self.ex_text_post_from_us1.encode(),self.ex_text_post_from_us2.encode()],
                "bucketname": "voter-bucket"
            },
        }
        want_msg_list = {
            "test1": self.ex_parsed_msg_single,
            "test2": self.ex_parsed_msg_mult,
        }
        #
        # TODO mock getting the body and skip that call?
        for key, test in msg_input.items():
            # print(test['comparison_type'])
            got_msg_list = em.get_msg_objs_list(test["msgs"], test["bucketname"])
            for msg in got_msg_list:
                for i, (k, v) in enumerate(msg):
                    if k == 'body_bytes':
                        msg.pop(i)
                        break
                self.assertEqual(k, 'body_bytes', "Body bytes missing get msg objects")
            # Remove body_bytes content from comparison
            self.assertEqual(want_msg_list[key], got_msg_list, "Get msg objects error")


    def test_parse_body(self):

        msg_input = {
            "test1": {
                "comparison_type": "Test getting body from multipart message",
                "msg_obj": email.parser.BytesParser().parsebytes(self.ex_binary_post_from_uk)
            },
            "test2": {
                "comparison_type": "Test getting body from single part message",
                    "msg_obj":    email.parser.BytesParser().parsebytes(b'What is the Voter Rights Act?\n'),
            }
        }
        want_msg_list = {
            "test1": [('Body', 'Full women voting rights passed in U.K.\n\n"We are here, not because we are law-breakers; we are here in our efforts to become law-makers."\n')],
            "test2": [('Body', 'What is the Voter Rights Act?\n')],
        }
        #
        for key, test in msg_input.items():
            # print(test['comparison_type'])
            got_msg_list = em.parse_body(test["msg_obj"])
            self.assertEqual(got_msg_list[-1][0], 'body_bytes', "Body bytes missing in test: " + test['comparison_type'])
            # Remove body_bytes content from comparison
            self.assertEqual(want_msg_list[key], got_msg_list[:-1], "Parse body error")

    # TODO test empty date and all the exceptions
    def test_parse_datestring(self):

        date_input = {
            "test1": {
                "comparison_type": "Test standard date format w/ 1 dig date and neg 8 hr GMT offset",
                "input": ("", "Sat, 6 Aug 1965 22:11:18 -0800")
            },
            "test2": {
            "comparison_type": "Test day month format w/o week day and w/ 2 dig date and pos 2 hr GMT offset",
            "input": ("", "15 Oct 2000 19:52:16 +0200"),
            },

            "test3": {
                "comparison_type":"Test standard date format w/ 2 dig date and pos 2 hr GMT offset",
                "input":("", "Wed, 19 May 1999 03:10:15 +0200")},
            "test4": {
                "comparison_type":"Test standard date format w/ 2 dig date and pos 1 hr GMT offset and timezone note",
                "input":("", "Tue, 13 Feb 2001 08:17:03 +0100 (MET)")},
            "test5": {
                "comparison_type": "Test day month format w/o week day w/ 1 dig date and 8 hr GMT offset",
                "input":("", "6 Nov 2006 11:11:19 -0800")},
            "test6": {
                "comparison_type": "Test standard date format w/ 2 dig date and no GMT offset and timezone note",
                "input": ("", "Wed, 25 Oct 2006 19:21:24 GMT")},
            "test7": {
                "comparison_type": "Test day month format w/o week day w/ 2 dig date and 8 hr GMT offset and timezone note",
                "input": ("", "25 May 2006 03:11:24 GMT") },
            "test8": {
                "comparison_type": "Test day of week day and mont w/ 1 dig date and nothing else",
                "input": ("", "Sat, 6 Aug")},
            # TODO following don't parse currently - need fixes and include in tests
            # "test8": (,"Sun, 05 Nov 2000 19:04:06 -050"),
            # "test10": (,"Sun, 05 Nov 2000 19:04:06  0000"),
            # "test11": (,"Sun, 05 Nov 2000 19:04:06  0000"),
            # "test12": (,"èøMJun, 26 Sep 2006 09:22:19 +0800")
        }
        want_date = {
            "test1": {'date': '1965-08-07 06:11:18',
                    'raw_date_string': 'Sat, 6 Aug 1965 22:11:18 -0800'},
            "test2": {'date': '2000-10-15 17:52:16', 'raw_date_string': '15 Oct 2000 19:52:16 +0200'},
            "test3": {'date': '1999-05-19 01:10:15',
                    'raw_date_string': 'Wed, 19 May 1999 03:10:15 +0200'},
            "test4": {'date': '2001-02-13 07:17:03',
                  'raw_date_string': 'Tue, 13 Feb 2001 08:17:03 +0100 (MET)'},
            "test5": {'date': '2006-11-06 19:11:19', 'raw_date_string': '6 Nov 2006 11:11:19 -0800'},
            "test6": {'date': '2006-10-25 19:21:24',
                    'raw_date_string': 'Wed, 25 Oct 2006 19:21:24 GMT'},
            "test7": {'date': '2006-05-25 03:11:24', 'raw_date_string': '25 May 2006 03:11:24 GMT'},
            "test8": {'date': '2020-08-06 07:00:00', 'raw_date_string': 'Sat, 6 Aug'}
            # "test9": "2000-11-05 19:04:06-05:00",
            # "test10": "2000-11-05 19:04:06+00:00",
            # "test11": "2000-11-05 19:04:06+00:00",
            # "test12": "2006-09-26 09:22:19+08:00"
        }

        for key, test in date_input.items():
            # print(test['comparison_type'])
            got_date = em.parse_datestring(test["input"])
            self.assertEqual(want_date[key], got_date, "Parse datestring error")

    def test_parse_contacts(self):
        pass

    def test_parse_references(self):
        pass

    def test_parse_everything_else(self):
        pass


    # TODO test one email address, multiple, with or with or without names, with or without symbols
    # TODO test references where there is one, none and multiple provided
    # Note the email should be DLPed
    def test_convert_msg_to_json(self):

        msg_input = {
            "test1": {
                "comparison_type":"Test processing msg list",
                "msg": self.ex_parsed_msg_single[0]
            }
        }
        want_json = {
            "test1": {'refs': [{'ref': '<voting-rights-id@mail.gmail.com>'}],
                    'references': '<voting-rights-id@mail.gmail.com>',
                    'raw_from_string': 'UK Parliment <uk.parliment@gmail.com>',
                    'from_name': 'uk parliment',
                    'from_email': 'uk.parliment@gmail.com',
                    'raw_to_string': 'Emmeline Pankhurst <emmeline.pankhurst@gmail.com>',
                    'to_name': 'emmeline pankhurst',
                    'to_email': 'emmeline.pankhurst@gmail.com',
                    'subject': 'Voting Rights',
                    'raw_date_string': 'Mon, July 2 1928 13:46:03 +0100',
                    'date': '1928-07-02 12:46:03',
                    'message_id': '<voting-rights-id@mail.gmail.com>',
                    'body': 'Full women voting rights passed in U.K.\n\n"We are here, not because we are law-breakers; we are here in our efforts to become law-makers."',
                    'references': '<voting-rights-id@mail.gmail.com>',
                    'list': 'pankhurst-bucket'},
        }
        #
        for key, test in msg_input.items():
            # print(test['comparison_type'])
            got_json = em.convert_msg_to_json(test["msg"])
            self.assertEqual(want_json[key], got_json, "Convert message to json error")


if __name__ == '__main__':
    unittest.main()