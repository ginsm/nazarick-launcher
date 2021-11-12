import { Response } from 'express';
import { TestObject } from './test-issuer';

import Chai from 'chai';
import ChaiHttp from 'chai-http';
Chai.use(ChaiHttp);

import Server from '../../../src/index';


// Just a simple wrapper that supports conditional chaining
export function chaiRequest(test: TestObject ) {
  if (test.route) {
    let req = Chai.request(Server).get(test.route);
    if (test.payload) req = req.send(test.payload);
    if (test.parse) req = req.buffer().parse(binaryParser);
    return req;
  }
  throw new Error('Malformed test object');
}

export function binaryParser(res: Response, cb: Function): void {
  res.setEncoding("binary");
  res.data = "";
  res.on("data", function (chunk) {
    res.data += chunk;
  });
  res.on("end", function () {
    cb(null, Buffer.from(res.data, "binary"));
  });
}