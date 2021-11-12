import Chai from 'chai';
import { chaiRequest } from './chai-request-wrapper';


export interface TestObject {
  route: string,
  status: number,
  payload?: (Record<string, any> | Array<any>),
  parse?: boolean,
  expectedFiles?: Array<string>,
  error?: string,
  callback?: Function,
}

// I suck at naming things
export function issuer(test: TestObject) {
  return (done) => {
    chaiRequest(test).end((err, res) => {
      if (err) done(err);
      Chai.expect(res).to.have.status(test.status);

      if (test.hasOwnProperty('error')) {
        const { error } = test;
        Chai.expect(res.body).to.have.property('error').equal(error);
        return done();
      } 

      const result = test.callback(res, test);
      Chai.expect(res).to.have.status(200);
      Chai.expect(result).to.be.true;
      return done();
    });
  };
}